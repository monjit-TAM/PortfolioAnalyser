"""Authentication service for API"""
import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import psycopg2
from psycopg2.extras import RealDictCursor

SECRET_KEY = os.environ.get("SESSION_SECRET", secrets.token_hex(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db_connection():
    return psycopg2.connect(os.environ.get("DATABASE_URL"))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if hashed_password.startswith("pbkdf2:"):
        import hashlib
        parts = hashed_password.split(":")
        if len(parts) >= 3:
            method = parts[0]
            iterations = int(parts[1].split("$")[0]) if "$" in parts[1] else 150000
            salt = parts[1].split("$")[1] if "$" in parts[1] else parts[1]
            stored_hash = parts[2]
            new_hash = hashlib.pbkdf2_hmac(
                'sha256',
                plain_password.encode(),
                salt.encode(),
                iterations
            ).hex()
            return new_hash == stored_hash
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def authenticate_user(email: str, password: str) -> Optional[dict]:
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
            if user and verify_password(password, user['password_hash']):
                return dict(user)
    finally:
        conn.close()
    return None


def create_user(email: str, password: str, full_name: Optional[str] = None) -> Optional[dict]:
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cur.fetchone():
                return None
            
            password_hash = get_password_hash(password)
            cur.execute(
                """INSERT INTO users (email, password_hash, full_name, created_at) 
                   VALUES (%s, %s, %s, NOW()) RETURNING id, email, full_name, created_at""",
                (email, password_hash, full_name)
            )
            user = cur.fetchone()
            conn.commit()
            return dict(user) if user else None
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_user_by_email(email: str) -> Optional[dict]:
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, email, full_name, created_at FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
            return dict(user) if user else None
    finally:
        conn.close()


def create_api_key(user_id: int, name: str, permissions: list) -> str:
    api_key = f"al_{secrets.token_hex(32)}"
    api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS api_keys (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    name VARCHAR(255),
                    key_hash VARCHAR(255) UNIQUE,
                    permissions TEXT[],
                    created_at TIMESTAMP DEFAULT NOW(),
                    last_used TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            cur.execute(
                """INSERT INTO api_keys (user_id, name, key_hash, permissions) 
                   VALUES (%s, %s, %s, %s)""",
                (user_id, name, api_key_hash, permissions)
            )
            conn.commit()
    finally:
        conn.close()
    
    return api_key


def validate_api_key(api_key: str) -> Optional[dict]:
    api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT ak.*, u.email, u.full_name 
                FROM api_keys ak 
                JOIN users u ON ak.user_id = u.id 
                WHERE ak.key_hash = %s AND ak.is_active = TRUE
            """, (api_key_hash,))
            result = cur.fetchone()
            
            if result:
                cur.execute(
                    "UPDATE api_keys SET last_used = NOW() WHERE key_hash = %s",
                    (api_key_hash,)
                )
                conn.commit()
                return dict(result)
    finally:
        conn.close()
    return None


def get_user_api_keys(user_id: int) -> list:
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, name, permissions, created_at, last_used, is_active 
                FROM api_keys WHERE user_id = %s ORDER BY created_at DESC
            """, (user_id,))
            return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def revoke_api_key(user_id: int, key_id: int) -> bool:
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE api_keys SET is_active = FALSE WHERE id = %s AND user_id = %s",
                (key_id, user_id)
            )
            conn.commit()
            return cur.rowcount > 0
    finally:
        conn.close()
