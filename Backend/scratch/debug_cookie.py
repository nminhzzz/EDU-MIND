import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Đọc file .env
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if line_str and not line_str.startswith("#") and "=" in line_str:
                key, val = line_str.split("=", 1)
                os.environ[key.strip()] = val.strip()

from fastapi import FastAPI, Depends, Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.testclient import TestClient
from typing import Optional

app = FastAPI()
bearer_scheme = HTTPBearer(auto_error=False)


def get_token_debug(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
):
    print("DEBUG get_token_debug:")
    print(f"  - Cookies: {request.cookies}")
    print(f"  - Headers: {dict(request.headers)}")
    print(f"  - Credentials: {credentials}")

    token = request.cookies.get("access_token")
    if token:
        print(f"  - Found token in cookie: {token[:20]}...")
        return token

    if credentials and credentials.credentials:
        print(f"  - Found token in header: {credentials.credentials[:20]}...")
        return credentials.credentials

    print("  - No token found anywhere!")
    raise HTTPException(status_code=401, detail="Not authenticated")


@app.get("/me")
def get_me(token: str = Depends(get_token_debug)):
    return {"token": token}


from fastapi import Response


@app.post("/login")
def login(response: Response):
    response.set_cookie(
        key="access_token", value="mocked_access_token_value", httponly=False
    )
    return {"message": "Logged in"}


def run_debug():
    client = TestClient(app)

    print("--- LOGIN ---")
    r_login = client.post("/login")
    print(f"Login Response: {r_login.json()}")
    print(f"Client Cookies: {client.cookies}")

    print("\n--- GET ME ---")
    r_me = client.get("/me")
    print(f"Get Me Response Code: {r_me.status_code}")
    print(f"Get Me Response Body: {r_me.text}")


if __name__ == "__main__":
    run_debug()
