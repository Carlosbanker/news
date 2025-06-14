import requests
import os
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"

def ask_model(prompt, system_instruction="You are a helpful assistant."):
    payload = {
        "inputs": f"[INST] <<SYS>>\n{system_instruction}\n<</SYS>>\n\n{prompt} [/INST]",
        "parameters": {"max_new_tokens": 500, "temperature": 0.7}
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()[0]["generated_text"]
    else:
        return f"Error {response.status_code}: {response.json()}"

# Test
if __name__ == "__main__":
    result = ask_model("Give me a news-style summary of the latest advancements in artificial intelligence.")
    print(result)
