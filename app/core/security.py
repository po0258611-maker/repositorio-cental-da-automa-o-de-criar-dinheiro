"""
AME - Security Layer
Auth, JWT, Rate Limit, Input Validation, Secrets protection
"""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_minutes: Optional[int] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes or settings.jwt_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    if credentials is None:
        return None
    try:
        payload = decode_token(credentials.credentials)
        return payload
    except HTTPException:
        return None

# Rate Limit simples em memória (para produção usar Redis)
from collections import defaultdict
import time

_rate_store = defaultdict(list)

def rate_limit(request: Request, limit: int = 100, window_seconds: int = 60):
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    window_start = now - window_seconds
    # limpa antigos
    _rate_store[client_ip] = [t for t in _rate_store[client_ip] if t > window_start]
    if len(_rate_store[client_ip]) >= limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")
    _rate_store[client_ip].append(now)

def sanitize_input(text: str, max_length: int = 5000) -> str:
    if not isinstance(text, str):
        raise HTTPException(status_code=400, detail="Invalid input type")
    text = text.strip()
    if len(text) > max_length:
        raise HTTPException(status_code=400, detail=f"Input too long (max {max_length})")
    # bloqueia tentativas básicas de injeção
    forbidden = ["<script", "javascript:", "data:text/html"]
    lower = text.lower()
    for f in forbidden:
        if f in lower:
            raise HTTPException(status_code=400, detail="Potentially unsafe input detected")
    return text

def mask_secret(value: str) -> str:
    if not value or len(value) < 8:
        return "***"
    return value[:4] + "***" + value[-4:]
