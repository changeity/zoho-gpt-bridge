
import os
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import httpx
import time

load_dotenv()

print("DEBUG: CLIENT_ID =", CLIENT_ID)
print("DEBUG: CLIENT_SECRET =", CLIENT_SECRET[:4] + "..." if CLIENT_SECRET else None)
print("DEBUG: REFRESH_TOKEN =", REFRESH_TOKEN[:4] + "..." if REFRESH_TOKEN else None)
print("DEBUG: WORKSPACE_ID =", WORKSPACE_ID)
print("DEBUG: API_DOMAIN =", API_DOMAIN)

app = FastAPI()

# Load environment variables
CLIENT_ID = os.getenv("ZOHO_CLIENT_ID")
CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("ZOHO_REFRESH_TOKEN")
WORKSPACE_ID = os.getenv("ZOHO_WORKSPACE_ID")
API_DOMAIN = os.getenv("ZOHO_API_DOMAIN", "https://www.zohoapis.com")

ACCESS_TOKEN = os.getenv("ZOHO_ACCESS_TOKEN")
TOKEN_EXPIRY = 0  # Epoch time when token expires

class SQLQuery(BaseModel):
    sql: str

async def refresh_access_token():
    global ACCESS_TOKEN, TOKEN_EXPIRY
    url = f"{API_DOMAIN}/oauth/v2/token"
    params = {
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, params=params)
        if response.status_code == 200:
            data = response.json()
            ACCESS_TOKEN = data["access_token"]
            TOKEN_EXPIRY = time.time() + int(data.get("expires_in", 3600)) - 60
        else:
            raise HTTPException(status_code=500, detail="Failed to refresh access token")

async def ensure_token():
    if not ACCESS_TOKEN or time.time() >= TOKEN_EXPIRY:
        await refresh_access_token()

@app.post("/query")
async def query_zoho(query: SQLQuery):
    await ensure_token()
    url = f"https://analyticsapi.zoho.com/restapi/v2/workspaces/{WORKSPACE_ID}/sql"
    headers = {
        "Authorization": f"Zoho-oauthtoken {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"sql": query.sql}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()
