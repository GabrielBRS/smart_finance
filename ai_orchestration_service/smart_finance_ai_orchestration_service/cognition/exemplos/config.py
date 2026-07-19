# config
import os

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://192.168.15.201:8000/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "nemotron")
LLM_API_KEY = os.getenv("LLM_API_KEY", "not-needed-on-prem")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nemotron-embed")