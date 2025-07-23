from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx

from db import get_db_connection  # ← işte burada db.py'yi kullanıyoruz

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

OLLAMA_API_URL = "http://localhost:11434/api/generate"

@app.get("/", response_class=HTMLResponse)
def get_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "bot_response": ""})

@app.post("/", response_class=HTMLResponse)
async def post_form(request: Request, user_input: str = Form(...)):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Önceki konuşmaları getir
        cursor.execute("SELECT role, content FROM messages ORDER BY id")
        history = cursor.fetchall()

        # Prompt oluştur
        full_prompt = ""
        for role, content in history:
            full_prompt += f"{role}: {content}\n"
        full_prompt += f"user: {user_input}\nassistant:"

        # Ollama'ya istek at
        async with httpx.AsyncClient() as client:
            response = await client.post(OLLAMA_API_URL, json={"model": "llama3", "prompt": full_prompt})
            bot_response = response.json().get("response", "Bot yanıt vermedi.")

        # Veritabanına yaz
        cursor.execute("INSERT INTO messages (role, content) VALUES (%s, %s)", ("user", user_input))
        cursor.execute("INSERT INTO messages (role, content) VALUES (%s, %s)", ("assistant", bot_response))
        conn.commit()

    except Exception as e:
        bot_response = f"Hata oluştu: {str(e)}"

    finally:
        if conn:
            conn.close()

    return templates.TemplateResponse("index.html", {"request": request, "bot_response": bot_response})
