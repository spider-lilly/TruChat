import base64
import json
import mimetypes
import os
import re
import time
from typing import Any, Tuple

from django.conf import settings
import requests


def load_image(image_input: Any) -> Tuple[bytes, str]:

    if not image_input:
        raise ValueError("Invalid image input: input data is empty or None.")

    image_bytes = b""
    mime_type = "image/jpeg"

    # Case 1: Uploaded bytes or bytearray
    if isinstance(image_input, (bytes, bytearray)):
        image_bytes = bytes(image_input)

    # Case 2: File-like object (e.g. Django UploadedFile / BytesIO)
    elif hasattr(image_input, "read") and callable(image_input.read):
        image_bytes = image_input.read()
        if hasattr(image_input, "seek") and callable(image_input.seek):
            image_input.seek(0)
        uploaded_mime = getattr(image_input, "content_type", None)
        file_name = getattr(image_input, "name", "")
        if uploaded_mime:
            mime_type = uploaded_mime
        elif file_name:
            guessed_mime = mimetypes.guess_type(file_name)[0]
            if guessed_mime:
                mime_type = guessed_mime

    # Case 3: Base64 string or file path
    elif isinstance(image_input, str):
        cleaned_str = image_input.strip()
        if not cleaned_str:
            raise ValueError("Invalid image input: text string is empty.")

        # Sub-case 3a: Base64 Data URI (e.g., data:image/png;base64,...)
        if cleaned_str.lower().startswith("data:image/"):
            match = re.match(
                r"^data:(image/[a-zA-Z0-9\+\-\.]+);base64,(.*)$",
                cleaned_str,
                re.DOTALL | re.IGNORECASE,
            )
            if not match:
                raise ValueError("Invalid base64 Data URI format.")
            mime_type = match.group(1)
            b64_data = match.group(2).strip()
            try:
                image_bytes = base64.b64decode(b64_data)
            except Exception as e:
                raise ValueError(f"Invalid base64 encoding in Data URI: {e}") from e

        # Sub-case 3b: File path
        elif os.path.exists(cleaned_str) and os.path.isfile(cleaned_str):
            guessed_mime = mimetypes.guess_type(cleaned_str)[0]
            if guessed_mime:
                mime_type = guessed_mime
            try:
                with open(cleaned_str, "rb") as f:
                    image_bytes = f.read()
            except Exception as e:
                raise ValueError(f"Failed to read image file at '{cleaned_str}': {e}") from e

        # Sub-case 3c: Raw base64 string
        else:
            try:
                image_bytes = base64.b64decode(cleaned_str, validate=True)
            except Exception as e:
                raise ValueError(f"Invalid image file path or base64 string: {e}") from e

    else:
        raise ValueError(
            f"Unsupported image input type: '{type(image_input).__name__}'. "
            "Supported types are bytes, file path, file-like object, or base64 string."
        )

    if not image_bytes:
        raise ValueError("Loaded image contains empty data (0 bytes).")

    # Detect mime type from magic bytes if possible
    if image_bytes.startswith(b"\x89PNG"):
        mime_type = "image/png"
    elif image_bytes.startswith(b"\xff\xd8\xff"):
        mime_type = "image/jpeg"
    elif image_bytes.startswith(b"GIF8"):
        mime_type = "image/gif"
    elif image_bytes.startswith(b"RIFF") and image_bytes[8:12] == b"WEBP":
        mime_type = "image/webp"

    return image_bytes, mime_type


def ocr_space_extract(image_bytes: bytes, mime_type: str) -> str:

    api_key = getattr(settings, "OCRAPI", None) or os.getenv("OCRAPI")
    if not api_key:
        raise ValueError("OCR.space API key is not configured in settings.OCRAPI.")

    url = "https://api.ocr.space/parse/image"
    payload = {
        "apikey": api_key,
        "language": "eng",
        "isOverlayRequired": False,
        "detectOrientation": True,
        "scale": True,
        "OCREngine": 2,
    }
    files = {
        "file": ("image", image_bytes, mime_type)
    }

    try:
        response = requests.post(url, data=payload, files=files, timeout=30)
    except requests.exceptions.Timeout as e:
        raise TimeoutError(f"OCR.space API request timed out: {e}") from e
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Network failure calling OCR.space API: {e}") from e

    if response.status_code != 200:
        raise RuntimeError(
            f"OCR.space API returned HTTP status {response.status_code}: {response.text}"
        )

    try:
        result = response.json()
    except Exception as e:
        raise RuntimeError(f"Failed to parse OCR.space API JSON response: {e}") from e

    if result.get("IsErroredOnProcessing"):
        err_msg = (
            result.get("ErrorMessage")
            or result.get("ErrorDetails")
            or "Unknown OCR.space processing error"
        )
        if isinstance(err_msg, list):
            err_msg = "; ".join(err_msg)
        raise RuntimeError(f"OCR.space API failure: {err_msg}")

    parsed_results = result.get("ParsedResults")
    if not parsed_results or not isinstance(parsed_results, list):
        raise ValueError("OCR response contained no parsed results.")

    extracted_chunks = [
        item.get("ParsedText", "")
        for item in parsed_results
        if isinstance(item, dict) and item.get("ParsedText")
    ]
    extracted_text = "".join(extracted_chunks)

    if not extracted_text or not extracted_text.strip():
        raise ValueError("Empty OCR response: no text extracted from image.")

    return extracted_text


def clean_ocr_text(text: str) -> str:
    """Perform deterministic cleanup on raw OCR text without using AI."""
    if not text:
        return ""

    # Fix broken line endings (\r\n or \r -> \n)
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove trailing spaces and collapse excessive spaces on each line
    cleaned_lines = []
    for line in normalized.split("\n"):
        collapsed = re.sub(r"[ \t]+", " ", line).strip()
        cleaned_lines.append(collapsed)

    joined = "\n".join(cleaned_lines)

    # Remove repeated blank lines (collapse 3+ newlines to 2 newlines)
    result = re.sub(r"\n{3,}", "\n\n", joined)

    return result.strip()


def format_output(text: str, output_format: str = "markdown") -> str:
    """Format text locally into markdown, json, plain_text, or latex."""
    fmt = (output_format or "markdown").lower().strip()

    if fmt == "markdown":
        return text
    elif fmt == "plain_text":
        return text
    elif fmt == "json":
        return json.dumps({"text": text}, ensure_ascii=False, indent=2)
    elif fmt == "latex":
        latex_escapes = {
            "\\": "\\textbackslash{}",
            "&": "\\&",
            "%": "\\%",
            "$": "\\$",
            "#": "\\#",
            "_": "\\_",
            "{": "\\{",
            "}": "\\}",
            "~": "\\textasciitilde{}",
            "^": "\\textasciicircum{}",
        }
        return "".join(latex_escapes.get(char, char) for char in text)
    else:
        valid_formats = ["markdown", "json", "plain_text", "latex"]
        raise ValueError(
            f"Unsupported output format: '{output_format}'. "
            f"Supported formats are: {', '.join(valid_formats)}"
        )


def process_image(image_input: Any, output_format: str = "markdown") -> dict:
    """Execute the full OCR pipeline for an input image.

    Pipeline: load_image -> ocr_space_extract -> clean_ocr_text -> format_output
    """
    start_time = time.time()

    image_bytes, mime_type = load_image(image_input)
    raw_text = ocr_space_extract(image_bytes, mime_type)
    cleaned_text = clean_ocr_text(raw_text)
    formatted_text = format_output(cleaned_text, output_format)

    processing_time_ms = round((time.time() - start_time) * 1000, 2)

    return {
        "status": "success",
        "text": raw_text,
        "formatted_text": formatted_text,
        "engine": "OCR.space",
        "processing_time_ms": processing_time_ms,
    }
