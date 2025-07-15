import os
import time
import traceback
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import httpx

load_dotenv()

# Load environment variables
CLIENT_ID = os.getenv("ZOHO_CLIENT_ID")
CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("ZOHO_REFRESH_TOKEN")
WORKSPACE_ID = os.getenv("ZOHO_WORKSPACE_ID")
API_DOMAIN = os.getenv("ZOHO_API_DOMAIN", "https://www.zohoapis.com")
OAUTH_DOMAIN = os.getenv("ZOHO_OAUTH_DOMAIN", "https://accounts.zoho.com")  # <-- Correct OAuth domain

print("DEBUG: CLIENT_ID =", CLIENT_ID)
print("DEBUG: CLIENT_SECRET =", CLIENT_SECRET[:4] + "..." if CLIENT_SECRET else None)
print("DEBUG: REFRESH_TOKEN =", REFRESH_TOKEN[:4] + "..." if REFRESH_TOKEN else None)
print("DEBUG: WORKSPACE_ID =", WORKSPACE_ID)
print("DEBUG: API_DOMAIN =", API_DOMAIN)
print("DEBUG: OAUTH_DOMAIN =", OAUTH_DOMAIN)

ACCESS_TOKEN = os.getenv("ZOHO_ACCESS_TOKEN")
TOKEN_EXPIRY = 0  # Epoch time when token expires

app = FastAPI()

class SQLQuery(BaseModel):
    sql: str

async def refresh_access_token():
    global ACCESS_TOKEN, TOKEN_EXPIRY
    url = f"{OAUTH_DOMAIN}/oauth/v2/token"
    params = {
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token"
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, params=params)
            if response.status_code == 200:
                data = response.json()
                ACCESS_TOKEN = data["access_token"]
                TOKEN_EXPIRY = time.time() + int(data.get("expires_in", 3600)) - 60
                print(f"[INFO] Access token refreshed successfully: expires in {data.get('expires_in')} seconds")
            else:
                text = response.text
                print(f"[ERROR] Failed to refresh access token: {response.status_code} {text}")
                raise HTTPException(status_code=500, detail="Failed to refresh access token")
    except Exception as e:
        print(f"[EXCEPTION] Exception during token refresh: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Exception during token refresh")

async def ensure_token():
    if not ACCESS_TOKEN or time.time() >= TOKEN_EXPIRY:
        print("[INFO] Access token expired or missing, refreshing...")
        await refresh_access_token()

@app.post("/query")
async def query_zoho(query: SQLQuery):
    try:
        await ensure_token()
        url = f"{API_DOMAIN}/analyticsapi/v2/workspaces/{WORKSPACE_ID}/sql"
        headers = {
            "Authorization": f"Zoho-oauthtoken {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {"sql": query.sql}
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code != 200:
                text = response.text
                print(f"[ERROR] Zoho API error: {response.status_code} {text}")
                raise HTTPException(status_code=response.status_code, detail=response.text)
            return response.json()
    except Exception as e:
        print(f"[EXCEPTION] Exception in /query: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")
