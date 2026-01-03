import razorpay
import os
from datetime import datetime, timedelta

MONTHLY_PRICE = 49900
DISCOUNTED_PRICE = 49900
CURRENCY = "INR"

def get_razorpay_client():
    key_id = os.environ.get('RAZORPAY_KEY_ID')
    key_secret = os.environ.get('RAZORPAY_KEY_SECRET')
    
    if not key_id or not key_secret:
        print(f"Razorpay keys missing - ID: {bool(key_id)}, Secret: {bool(key_secret)}")
        return None
    
    return razorpay.Client(auth=(key_id, key_secret))

def create_order(amount=DISCOUNTED_PRICE, currency=CURRENCY, receipt=None):
    client = get_razorpay_client()
    if not client:
        print("Razorpay client not initialized - check API keys")
        return None
    
    if receipt is None:
        receipt = f"order_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    order_data = {
        "amount": amount,
        "currency": currency,
        "receipt": receipt,
        "payment_capture": 1
    }
    
    try:
        order = client.order.create(data=order_data)
        return order
    except razorpay.errors.BadRequestError as e:
        print(f"Razorpay BadRequest: {e}")
        return {"error": str(e)}
    except razorpay.errors.ServerError as e:
        print(f"Razorpay ServerError: {e}")
        return {"error": "Payment gateway temporarily unavailable"}
    except Exception as e:
        error_msg = str(e)
        print(f"Error creating order: {error_msg}")
        if "Authentication" in error_msg or "401" in error_msg:
            return {"error": "Authentication failed. Please verify Razorpay API keys in your dashboard."}
        return {"error": error_msg}

def verify_payment_signature(order_id, payment_id, signature):
    client = get_razorpay_client()
    if not client:
        return False
    
    try:
        params = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }
        client.utility.verify_payment_signature(params)
        return True
    except razorpay.errors.SignatureVerificationError:
        return False
    except Exception as e:
        print(f"Error verifying signature: {e}")
        return False

def get_payment_details(payment_id):
    client = get_razorpay_client()
    if not client:
        return None
    
    try:
        payment = client.payment.fetch(payment_id)
        return payment
    except Exception as e:
        print(f"Error fetching payment: {e}")
        return None
