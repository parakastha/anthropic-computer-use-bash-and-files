import os
from dotenv import load_dotenv

load_dotenv()
print(f"ANTHROPIC_API_KEY: {os.environ.get('ANTHROPIC_API_KEY')}")
