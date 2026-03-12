from email import message
import json
import re
import sys
import traceback
from typing import List

from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama3.2",
    temperature=0,
)


def invoke_llm(prompt: str, messages: List = None):
    try:
        if messages and len(messages):
            messages = messages
        else:
            messages = [{"role": "user", "content": prompt}]

        response = llm.invoke(messages)

        return response.content.strip()
    except Exception as e:
        print(f"[ERROR] LLM invocation failed: {e}")
        traceback.print_exc()
        # sys.exit(1)


def extract_json(text: str):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No valid JSON found in response")
    return json.loads(match.group())
