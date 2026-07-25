import html
import logging
import re
import unicodedata
from typing import Any

import ftfy
from bs4 import BeautifulSoup
from markdown import markdown

logger = logging.getLogger(__name__)


URL_PATTERN = re.compile(
    r"https?://\S+|www\.\S+",
    re.IGNORECASE,
)

MARKDOWN_LINK_PATTERN = re.compile(
    r"\[([^\]]+)\]\(([^)]+)\)"
)

MULTISPACE_PATTERN = re.compile(r"\s+")

REPEATED_PUNCT_PATTERN = re.compile(r"([!?.,])\1+")

ZERO_WIDTH_PATTERN = re.compile(
    r"[\u200B-\u200D\uFEFF]"
)

EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F700-\U0001F77F"
    "\U0001F780-\U0001F7FF"
    "\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FA6F"
    "\U0001FA70-\U0001FAFF"
    "\u2600-\u26FF"
    "\u2700-\u27BF"
    "]+",
    flags=re.UNICODE,
)


def clean_text(
    text: str,
    *,
    remove_urls: bool = False,
    remove_emojis: bool = True,
    html_input: bool = False,
) -> dict[str, Any]:
    """
    Generic text cleaner.

    Safe for:
    - Claims
    - News articles
    - Wikipedia
    - Tavily snippets
    - GDELT results

    Does NOT:
    - Lemmatize
    - Lowercase
    - Remove stopwords
    - Normalize entities
    """

    try:

        if text is None:
            logger.warning("clean_text received None.")
            return {
                "cleaned_text": "",
                "urls": [],
                "had_html": False,
                "had_markdown": False,
            }

        if not isinstance(text, str):
            text = str(text)

        text = text.strip()

        if not text:
            return {
                "cleaned_text": "",
                "urls": [],
                "had_html": False,
                "had_markdown": False,
            }


        urls = URL_PATTERN.findall(text)

        text = ftfy.fix_text(text)
        text = unicodedata.normalize("NFKC", text)

        text = html.unescape(text)

        had_html = html_input

        if html_input:
            soup = BeautifulSoup(text, "html.parser")
            text = soup.get_text(separator=" ")

        markdown_chars = ("**", "__", "#", "`", "[", "]", "(")

        had_markdown = any(char in text for char in markdown_chars)

        if had_markdown:

            text = MARKDOWN_LINK_PATTERN.sub(r"\1", text)

            text = BeautifulSoup(
                markdown(text),
                "html.parser",
            ).get_text(separator=" ")


        text = ZERO_WIDTH_PATTERN.sub("", text)

        text = (
            text.replace("“", '"')
            .replace("”", '"')
            .replace("‘", "'")
            .replace("’", "'")
        )

        text = (
            text.replace("–", "-")
            .replace("—", "-")
            .replace("−", "-")
        )

        if remove_urls:
            text = URL_PATTERN.sub("", text)

        if remove_emojis:
            text = EMOJI_PATTERN.sub("", text)

        text = REPEATED_PUNCT_PATTERN.sub(r"\1", text)

        text = MULTISPACE_PATTERN.sub(" ", text)

        return {
            "cleaned_text": text.strip(),
            "urls": urls,
            "had_html": had_html,
            "had_markdown": had_markdown,
        }

    except Exception:

        logger.exception("Unexpected error while cleaning text.")

        return {
            "cleaned_text": text.strip() if isinstance(text, str) else "",
            "urls": [],
            "had_html": False,
            "had_markdown": False,
        }