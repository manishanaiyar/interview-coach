import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load the .env file to get the API key
load_dotenv()

try:
    # Configure the SDK with your key
    genai.configure(api_key=os.getenv("LLM_API_KEY"))

    print("Finding available models that support 'generateContent'...\n")

    # List all models and find the ones that can generate text
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)

except Exception as e:
    print(f"An error occurred: {e}")
    print("\nPlease double-check that your LLM_API_KEY in the .env file is correct.")