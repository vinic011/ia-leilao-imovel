from openai import OpenAI
from dotenv import load_dotenv
import os
from var import vars
import time

load_dotenv()

open_ai_key = os.getenv("OPENAI_API_KEY")

with open(f"data/detail/{vars['cidade'].lower()}_{vars['estado'].lower()}/{vars['imovel']}.html", "r", encoding="utf-8") as f:
    detail = f.read()

client = OpenAI(api_key=open_ai_key)

file_id = vars["edital_file_id"]
state = vars["estado"]
city = vars["cidade"]
assistant_id = vars["assistant_id"]


thread = client.beta.threads.create()
thread_id = thread.id
print("thread", thread_id)

message = client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=f"Esta é a descrição resumida do imóvel: {detail}",
    attachments=[
        {
            "file_id": file_id,
            "tools": [{"type": "file_search"}]
        }
    ]
)


run = client.beta.threads.runs.create_and_poll(
    thread_id=thread_id,
    assistant_id=assistant_id
)

time.sleep(5)

messages = client.beta.threads.messages.list(thread_id=thread_id)
for msg in messages.data:
    if msg.role == "assistant":
        print(f"Assistant: {msg.content[0].text.value}")
        break
