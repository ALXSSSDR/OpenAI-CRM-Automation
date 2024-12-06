import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    WAZZUP_API_KEY = os.getenv("WAZZUP_API_KEY")
    AMOCRM_ACCESS_TOKEN = os.getenv("AMOCRM_ACCESS_TOKEN")
    WAZZUP_API_URL = "https://api.wazzup24.com/v3/message"
    WAZZUP_CHANNEL_ID = "5e157aae-9b7a-4361-9b07-3d94e1cdf5a8"
    AMOCRM_URL = "https://acc524e049130cf3.amocrm.ru"
    TOKEN_COST_IN_GPT4O = 2.50 / 10**6
    TOKEN_COST_OUT_GPT4O = 10.00 / 10**6
    TOKEN_COST_IN_GPT4_MINI = 0.150 / 10**6
    TOKEN_COST_OUT_GPT4_MINI = 0.600 / 10**6
    MODEL_GPT4O = "gpt-4o"
    MODEL_GPT4OMINI = "gpt-4o-mini"
    MAX_TOKENS = 3500
    PORT = int(os.getenv("PORT", 8080))