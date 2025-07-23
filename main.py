from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

OLLAMA_API_URL = "http://localhost:11434/api/generate"

# Basit bir oturum için konuşma geçmişini tutan değişken
conversation_history = []

@app.get("/", response_class=HTMLResponse)
def get_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "bot_response": ""})

@app.post("/", response_class=HTMLResponse)
async def post_form(request: Request, user_input: str = Form(...)):
    # Geçmişi tek bir stringe çevir
    history_prompt = "\n".join(
        [f"Kullanıcı: {entry['user']}\nBot: {entry['bot']}" for entry in conversation_history]
    )

    full_prompt = f"{history_prompt}\nKullanıcı: {user_input}\nBot:"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(OLLAMA_API_URL, json={
                "model": "llama3",
                "prompt": full_prompt,
                "stream": False
            })
            response.raise_for_status()
            response_json = response.json()
            bot_reply = response_json.get("response", "Bot bir şey söylemedi.")
        except Exception as e:
            bot_reply = f"Hata oluştu: {str(e)}"

    # Geçmişe ekle
    conversation_history.append({
        "user": user_input,
        "bot": bot_reply
    })

    return templates.TemplateResponse("index.html", {"request": request, "bot_response": bot_reply})
