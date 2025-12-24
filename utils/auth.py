import os
import hashlib
import secrets
from datetime import datetime
from utils.database import Database

class AuthManager:
    def __init__(self):
        self.db = Database()
    
    def _hash_password(self, password: str, salt: str = None) -> tuple:
        if salt is None:
            salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        return f"{salt}${password_hash}", salt
    
    def _verify_password(self, password: str, stored_hash: str) -> bool:
        try:
            salt, hash_value = stored_hash.split('$')
            new_hash, _ = self._hash_password(password, salt)
            return new_hash == stored_hash
        except:
            return False
    
    def signup(self, email: str, password: str, full_name: str = None, phone: str = None) -> dict:
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()
            
            cur.execute("SELECT id FROM users WHERE email = %s", (email.lower(),))
            if cur.fetchone():
                cur.close()
                conn.close()
                return {'success': False, 'message': 'Email already registered'}
            
            password_hash, _ = self._hash_password(password)
            
            cur.execute('''
                INSERT INTO users (email, password_hash, full_name, phone, created_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            ''', (email.lower(), password_hash, full_name, phone, datetime.now()))
            
            user_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
            
            return {
                'success': True,
                'message': 'Account created successfully',
                'user_id': user_id,
                'email': email.lower(),
                'full_name': full_name
            }
        except Exception as e:
            return {'success': False, 'message': f'Registration failed: {str(e)}'}
    
    def login(self, email: str, password: str) -> dict:
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()
            
            cur.execute('''
                SELECT id, email, password_hash, full_name, phone, is_admin 
                FROM users WHERE email = %s
            ''', (email.lower(),))
            
            user = cur.fetchone()
            
            if not user:
                cur.close()
                conn.close()
                return {'success': False, 'message': 'Invalid email or password'}
            
            user_id, user_email, password_hash, full_name, phone, is_admin = user
            
            if not self._verify_password(password, password_hash):
                cur.close()
                conn.close()
                return {'success': False, 'message': 'Invalid email or password'}
            
            cur.execute('UPDATE users SET last_login = %s WHERE id = %s', (datetime.now(), user_id))
            conn.commit()
            cur.close()
            conn.close()
            
            return {
                'success': True,
                'message': 'Login successful',
                'user_id': user_id,
                'email': user_email,
                'full_name': full_name,
                'is_admin': is_admin or False
            }
        except Exception as e:
            return {'success': False, 'message': f'Login failed: {str(e)}'}
    
    def get_user(self, user_id: int) -> dict:
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()
            
            cur.execute('''
                SELECT id, email, full_name, phone, created_at, last_login 
                FROM users WHERE id = %s
            ''', (user_id,))
            
            user = cur.fetchone()
            cur.close()
            conn.close()
            
            if user:
                return {
                    'id': user[0],
                    'email': user[1],
                    'full_name': user[2],
                    'phone': user[3],
                    'created_at': user[4],
                    'last_login': user[5]
                }
            return None
        except:
            return None
