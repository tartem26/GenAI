import asyncio
import time
import traceback
import json
import openai
import random
import requests

from hume import HumeStreamClient
from hume.models.config import LanguageConfig

from flask import Flask
api_key="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"

from typing import Any, Dict, List
app = Flask(__name__)


def print_emotions(emotions: List[Dict[str, Any]]) -> None:
    emotion_map = {e["name"]: e["score"] for e in emotions}
    for emotion in ["Joy", "Sadness", "Anger"]:
        print(f"- {emotion}: {emotion_map[emotion]:4f}")

text_sample = "Am I sucidal"

async def main():
    try:
        client = HumeStreamClient("EbATLlzvw9OCziDcIGrA4gH50gSjFPpuvSxm0TPbaiS6cnSm")
        config = LanguageConfig(granularity="sentence")
        async with client.connect([config]) as socket:
            result = await socket.send_text(text_sample)
            emotions = result["language"]["predictions"][0]["emotions"]
            print(f"\n{text_sample}")
            print_emotions(emotions)
            data = {
                "text_sample": text_sample,
                "emotions": {e["name"]: e["score"] for e in emotions if e["name"] in ["Joy", "Sadness", "Anger"]}
            }

            # Save the data to a JSON file
            with open("./score.json", "w") as json_file:
                json.dump(data, json_file, indent=4)
    except Exception:
        print(traceback.format_exc())

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

openai.api_key = api_key

with open("./score.json", 'r') as file:
    data = json.load(file)
    text_sample = data['text_sample']
    emotions = data['emotions']

# Construct the prompt
prompt = f'Give a response to "{text_sample}" on this scale: Anger - {emotions["Anger"]}, Joy - {emotions["Joy"]}, Sadness - {emotions["Sadness"]}, which increases the joyness and decreases person\'s anger and sadness, if the out the the 3 emotions if angry is highest help with a response which helps with anger control, it the resonse has joyness at the highest it should appreciate the person and if the highest is sadness then it should help the person cope up with his sadness.'

# Use the OpenAI API to get a response
response = openai.Completion.create(
    engine="text-davinci-003",
    prompt=prompt,
    max_tokens=700  # You can adjust this to control the response length
)

# Extract the generated response from the API
generated_response = response.choices[0].text

# Print the response

def get_data():
    return {
        "output":generated_response
    }

if __name__ == '__main__':
    app.run()