from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
from datetime import datetime

from db import get_db_connection  # ← işte burada db.py'yi kullanıyoruz

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

OLLAMA_API_URL = "http://localhost:11434/api/generate"

def get_simple_response(user_input: str) -> str:
    """Ollama olmadığında basit yanıtlar verir"""
    responses = [
        "Merhaba! Ben Berkay Bot. Size nasıl yardımcı olabilirim?",
        "Bu konuda size yardımcı olmaya çalışacağım.",
        "İlginç bir soru! Düşünmem gerekiyor.",
        "Bu konuda daha fazla bilgi verebilirim.",
        "Teşekkürler! Başka bir sorunuz var mı?",
        "Anlıyorum. Size nasıl yardımcı olabilirim?",
        "Bu konuda size rehberlik edebilirim.",
        "Harika bir soru! Düşünelim..."
    ]
    import random
    return random.choice(responses)

def create_better_prompt(user_input: str, history: list) -> str:
    """Daha iyi prompt oluşturur"""
    system_prompt = """Sen Berkay Bot adında yardımcı bir Türkçe AI asistanısın. 
    Kısa, net ve Türkçe yanıtlar ver. 
    Samimi ve dostane bir ton kullan."""
    
    # Konuşma geçmişini ekle
    conversation = ""
    for role, content in history[-5:]:  # Son 5 mesajı al
        if role == "user":
            conversation += f"Kullanıcı: {content}\n"
        else:
            conversation += f"Sen: {content}\n"
    
    full_prompt = f"{system_prompt}\n\n{conversation}Kullanıcı: {user_input}\nSen:"
    return full_prompt

@app.get("/", response_class=HTMLResponse)
def get_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "bot_response": ""})

@app.get("/tests", response_class=HTMLResponse)
def get_tests(request: Request):
    conn = None
    tests = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, description, created_by, created_at FROM tests ORDER BY created_at DESC")
        tests = cursor.fetchall()
    except Exception as e:
        print(f"Test listesi hatası: {e}")
    finally:
        if conn:
            conn.close()
    
    return templates.TemplateResponse("tests.html", {"request": request, "tests": tests})

@app.post("/tests", response_class=HTMLResponse)
async def add_test(request: Request, title: str = Form(...), description: str = Form(...), created_by: str = Form(...)):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tests (title, description, created_by, created_at) VALUES (?, ?, ?, ?)", 
                      (title, description, created_by, datetime.now()))
        conn.commit()
    except Exception as e:
        print(f"Test ekleme hatası: {e}")
    finally:
        if conn:
            conn.close()
    
    return await get_tests(request)

@app.post("/", response_class=HTMLResponse)
async def post_form(request: Request, user_input: str = Form(...)):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Önceki konuşmaları getir
        cursor.execute("SELECT role, content FROM messages ORDER BY id")
        history = cursor.fetchall()

        # Ollama'ya istek atmayı dene
        bot_response = ""
        try:
            # Daha iyi prompt oluştur
            full_prompt = create_better_prompt(user_input, history)
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(OLLAMA_API_URL, json={
                    "model": "llama3", 
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 200
                    }
                })
                
                if response.status_code == 200:
                    response_data = response.json()
                    bot_response = response_data.get("response", "Bot yanıt vermedi.")
                    # Yanıtı temizle
                    bot_response = bot_response.strip()
                    if not bot_response:
                        bot_response = get_simple_response(user_input)
                else:
                    bot_response = get_simple_response(user_input)
        except Exception as e:
            print(f"Ollama hatası: {e}")
            bot_response = get_simple_response(user_input)

        # Veritabanına yaz (SQLite için ? kullan)
        cursor.execute("INSERT INTO messages (role, content) VALUES (?, ?)", ("user", user_input))
        cursor.execute("INSERT INTO messages (role, content) VALUES (?, ?)", ("assistant", bot_response))
        conn.commit()

    except Exception as e:
        bot_response = f"Hata oluştu: {str(e)}"

    finally:
        if conn:
            conn.close()

    return templates.TemplateResponse("index.html", {"request": request, "bot_response": bot_response})
