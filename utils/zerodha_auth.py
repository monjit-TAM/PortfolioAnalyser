"""Zerodha Kite API authentication helper"""
import os
import streamlit as st
from kiteconnect import KiteConnect

def get_zerodha_login_url():
    """Generate Zerodha login URL"""
    api_key = os.environ.get('ZERODHA_API_KEY')
    if not api_key:
        return None
    
    kite = KiteConnect(api_key=api_key)
    return kite.login_url()

def generate_access_token(request_token):
    """Generate access token from request token"""
    api_key = os.environ.get('ZERODHA_API_KEY')
    api_secret = os.environ.get('ZERODHA_API_SECRET')
    
    if not api_key or not api_secret:
        return None, "API credentials not configured"
    
    try:
        kite = KiteConnect(api_key=api_key)
        data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = data['access_token']
        return access_token, None
    except Exception as e:
        return None, str(e)

def is_zerodha_configured():
    """Check if Zerodha is configured with access token"""
    return bool(os.environ.get('ZERODHA_ACCESS_TOKEN'))

def render_zerodha_setup():
    """Render Zerodha setup UI in sidebar or settings"""
    api_key = os.environ.get('ZERODHA_API_KEY')
    api_secret = os.environ.get('ZERODHA_API_SECRET')
    access_token = os.environ.get('ZERODHA_ACCESS_TOKEN')
    
    if not api_key or not api_secret:
        st.warning("Zerodha API credentials not configured")
        return
    
    if access_token:
        st.success("Zerodha connected")
        return
    
    st.info("Zerodha login required for live prices")
    
    login_url = get_zerodha_login_url()
    if login_url:
        st.markdown(f"[Login to Zerodha]({login_url})")
        st.caption("After login, paste the request token from the redirect URL")
        
        request_token = st.text_input("Request Token", key="zerodha_request_token")
        if st.button("Generate Access Token"):
            if request_token:
                token, error = generate_access_token(request_token)
                if token:
                    st.success("Access token generated! Add this to your secrets:")
                    st.code(f"ZERODHA_ACCESS_TOKEN={token}")
                    st.info("Add the above as a secret, then restart the app")
                else:
                    st.error(f"Failed: {error}")
            else:
                st.error("Please enter the request token")
