import os
import requests
from dotenv import load_dotenv
load_dotenv()

class OpenRouterClient():
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
