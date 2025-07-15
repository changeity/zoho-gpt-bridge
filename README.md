# 📊 GPT-Zoho Analytics Bridge

This is a **FastAPI server** that allows a **Custom GPT** (like ChatGPT Plus) to run **SQL queries** directly on your **Zoho Analytics** workspace via secure API calls.

---

## ✅ Features

- Connects GPT to Zoho Analytics
- Secure token refresh with `.env` credentials
- Accepts SQL via `/query` endpoint
- Cloud-deployable (Render, Railway, etc.)

---

## 🚀 How to Deploy

1. Clone this repo  
2. Create a `.env` file (see `.env.example`) and add your secrets:
   ```
   ZOHO_CLIENT_ID=...
   ZOHO_CLIENT_SECRET=...
   ZOHO_REFRESH_TOKEN=...
   ZOHO_WORKSPACE_ID=...
   ZOHO_API_DOMAIN=https://www.zohoapis.com
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run locally:
   ```
   uvicorn main:app --reload
   ```

---

## 🛠️ /query Endpoint

- **POST** `/query`
- **Body**:
  ```json
  {
    "sql": "SELECT * FROM YourTable LIMIT 10"
  }
  ```

---

## 🔐 Security Notes

- Never commit `.env` to GitHub.
- Add `.env` to `.gitignore` (already included).

---

## 🤖 GPT Integration

Use this URL as your **tool endpoint** in your [Custom GPT](https://chat.openai.com/gpts) setup via the **OpenAPI** schema.