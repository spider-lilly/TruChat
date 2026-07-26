from django.conf import settings
from google import genai


def get_genai_client() -> genai.Client:
    api_key = settings.API_KEY
    return genai.Client(api_key=api_key)