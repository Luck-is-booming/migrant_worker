import hmac
import hashlib
import base64

def generate_esewa_signature(total_amount, transaction_uuid, product_code, secret_key):
    """
    Generates HMAC-SHA256 signature base64 encoded for eSewa v2.
    Format string order must be exact: total_amount, transaction_uuid, product_code
    """
    message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
    hash_obj = hmac.new(
        secret_key.encode('utf-8'), 
        message.encode('utf-8'), 
        hashlib.sha256
    ).digest()
    return base64.b64encode(hash_obj).decode('utf-8')