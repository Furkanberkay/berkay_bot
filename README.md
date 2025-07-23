# Berkay Bot - AI Chatbot

Bu proje, Ollama API kullanarak yapay zeka chatbot'u oluşturan bir FastAPI uygulamasıdır.

## Kurulum

1. **Python bağımlılıklarını yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Veritabanını başlatın:**
   ```bash
   python db.py
   ```

3. **Ollama'yı kurun ve çalıştırın:**
   - [Ollama](https://ollama.ai/)'yı indirin ve kurun
   - Llama2 modelini yükleyin:
     ```bash
     ollama pull llama2
     ```
   - Ollama servisini başlatın:
     ```bash
     ollama serve
     ```

## Çalıştırma

```bash
uvicorn main:app --reload
```

Uygulama http://localhost:8000 adresinde çalışacaktır.

## Özellikler

- FastAPI ile modern web API
- SQLite veritabanında konuşma geçmişi saklama
- Ollama API ile yapay zeka yanıtları
- Basit ve kullanıcı dostu arayüz
- Gerçek zamanlı chat deneyimi

## Sorun Giderme

- **Ollama API hatası:** Ollama servisinin çalıştığından ve llama2 modelinin yüklendiğinden emin olun
- **Port çakışması:** 8000 portu kullanımdaysa farklı bir port belirtin: `uvicorn main:app --reload --port 8001`
- **Veritabanı hatası:** `python db.py` komutunu çalıştırarak veritabanını yeniden oluşturun 