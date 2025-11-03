import os
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

file = client.files.create(
    file=open("edital.pdf", "rb"),
    purpose="assistants" 
)

with open("config.json", "r") as f:
    config = json.load(f)
    config["edital_file_id"] = file.id

with open("config.json", "w") as f:
    json.dump(config, f, indent=4)
    

