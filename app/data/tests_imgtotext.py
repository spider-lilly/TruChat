import base64
import io
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.conf import settings

from data.services.imgtotext import (
    clean_ocr_text,
    format_output,
    load_image,
    ocr_space_extract,
    process_image,
)


class ImgToTextTestCase(unittest.TestCase):

    def test_load_image_bytes(self):
        sample_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        data, mime = load_image(sample_bytes)
        self.assertEqual(data, sample_bytes)
        self.assertEqual(mime, "image/png")

    def test_load_image_file_object(self):
        file_obj = io.BytesIO(b"\xff\xd8\xff\xe0\x00\x10JFIF")
        file_obj.name = "test.jpg"
        data, mime = load_image(file_obj)
        self.assertEqual(data, b"\xff\xd8\xff\xe0\x00\x10JFIF")
        self.assertEqual(mime, "image/jpeg")

    def test_load_image_file_path(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR")
            tmp_path = tmp.name

        try:
            data, mime = load_image(tmp_path)
            self.assertEqual(data, b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR")
            self.assertEqual(mime, "image/png")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_load_image_base64_uri(self):
        raw_bytes = b"\xff\xd8\xffsample_image_bytes"
        b64_str = base64.b64encode(raw_bytes).decode("utf-8")
        data_uri = f"data:image/jpeg;base64,{b64_str}"
        data, mime = load_image(data_uri)
        self.assertEqual(data, raw_bytes)
        self.assertEqual(mime, "image/jpeg")

    def test_load_image_raw_base64(self):
        raw_bytes = b"\x89PNG\r\n\x1a\n"
        b64_str = base64.b64encode(raw_bytes).decode("utf-8")
        data, mime = load_image(b64_str)
        self.assertEqual(data, raw_bytes)
        self.assertEqual(mime, "image/png")

    def test_load_image_invalid(self):
        with self.assertRaises(ValueError):
            load_image(None)
        with self.assertRaises(ValueError):
            load_image("")
        with self.assertRaises(ValueError):
            load_image("invalid_non_existent_file_path_xyz_123!!")

    @patch.object(settings, "OCRAPI", "test_api_key")
    @patch("requests.post")
    def test_ocr_space_extract_success(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "OCRExitCode": 1,
            "IsErroredOnProcessing": False,
            "ParsedResults": [
                {"ParsedText": "Extracted Claim Text\r\nLine Two  "}
            ],
        }
        mock_post.return_value = mock_resp

        text = ocr_space_extract(b"dummy_bytes", "image/jpeg")
        self.assertEqual(text, "Extracted Claim Text\r\nLine Two  ")
        mock_post.assert_called_once()

    @patch.object(settings, "OCRAPI", "")
    def test_ocr_space_extract_missing_key(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(ValueError):
                ocr_space_extract(b"dummy_bytes", "image/jpeg")

    @patch.object(settings, "OCRAPI", "test_api_key")
    @patch("requests.post")
    def test_ocr_space_extract_api_error(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "IsErroredOnProcessing": True,
            "ErrorMessage": ["API limit exceeded"],
        }
        mock_post.return_value = mock_resp

        with self.assertRaises(RuntimeError):
            ocr_space_extract(b"dummy_bytes", "image/jpeg")

    @patch.object(settings, "OCRAPI", "test_api_key")
    @patch("requests.post")
    def test_ocr_space_extract_empty_response(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "IsErroredOnProcessing": False,
            "ParsedResults": [{"ParsedText": "   "}],
        }
        mock_post.return_value = mock_resp

        with self.assertRaises(ValueError):
            ocr_space_extract(b"dummy_bytes", "image/jpeg")

    def test_clean_ocr_text(self):
        dirty_text = "  First  Line   \r\n\r\n\r\n\r\n  Second   Line  "
        cleaned = clean_ocr_text(dirty_text)
        self.assertEqual(cleaned, "First Line\n\nSecond Line")

    def test_format_output(self):
        text = "Sample text & 100% test"

        # markdown
        self.assertEqual(format_output(text, "markdown"), text)
        # plain_text
        self.assertEqual(format_output(text, "plain_text"), text)
        # json
        json_out = format_output(text, "json")
        self.assertIn('"text": "Sample text & 100% test"', json_out)
        # latex
        latex_out = format_output(text, "latex")
        self.assertEqual(latex_out, r"Sample text \& 100\% test")
        # invalid
        with self.assertRaises(ValueError):
            format_output(text, "yaml")

    @patch.object(settings, "OCRAPI", "test_api_key")
    @patch("requests.post")
    def test_process_image_pipeline(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "IsErroredOnProcessing": False,
            "ParsedResults": [{"ParsedText": "  Test   OCR   Result  "}],
        }
        mock_post.return_value = mock_resp

        sample_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        result = process_image(sample_bytes, output_format="markdown")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["text"], "  Test   OCR   Result  ")
        self.assertEqual(result["formatted_text"], "Test OCR Result")
        self.assertEqual(result["engine"], "OCR.space")
        self.assertIn("processing_time_ms", result)
        self.assertIsInstance(result["processing_time_ms"], float)
