import razorpay
import os
from datetime import datetime, timedelta

RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET')

MONTHLY_PRICE = 49900
DISCOUNTED_PRICE = 49900
CURRENCY = "INR"

def get_razorpay_client():
    if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
        return None
    return razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

def create_order(amount=DISCOUNTED_PRICE, currency=CURRENCY, receipt=None):
    client = get_razorpay_client()
    if not client:
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
    except Exception as e:
        print(f"Error creating order: {e}")
        return None

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
