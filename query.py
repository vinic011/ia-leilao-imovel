from openai import OpenAI
from dotenv import load_dotenv
import os
from var import vars
import time
import pytesseract
from pdf2image import convert_from_path

# lendo matricula
paginas = convert_from_path(f"data/detail/{vars['cidade'].lower()}_{vars['estado'].lower()}/{vars['imovel']}.pdf")
matricula_imovel = ""
for pagina in paginas:
    matricula_imovel += pytesseract.image_to_string(pagina) + "\n"

print(len(matricula_imovel))
matricula_imovel = matricula_imovel[:1500]
#lendo detalhe
with open(f"data/detail/{vars['cidade'].lower()}_{vars['estado'].lower()}/{vars['imovel']}.html", "r", encoding="utf-8") as f:
    detail = f.read()

load_dotenv()

open_ai_key = os.getenv("OPENAI_API_KEY")
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
    content=f"Esta é a descrição resumida do imóvel: {detail}, matricula do imóvel: {matricula_imovel}.",
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

time.sleep(10)

# Recupera mensagens
messages = client.beta.threads.messages.list(thread_id=thread_id)

print("\n--- Resposta do Assistant ---\n")
for msg in messages.data:
    if msg.role == "assistant":
        for content in msg.content:
            if content.type == "text":
                print(content.text.value)
            elif content.type == "output_text":
                print(content.output_text.value)
            else:
                print("Outro tipo de conteúdo:", content)

