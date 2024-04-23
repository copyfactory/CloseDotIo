import hashlib
import hmac
import json


def is_webhook_data_valid(
    close_sig_timestamp: str, close_sig_hash: str, payload: dict, signature_key: str
) -> bool:
    data = close_sig_timestamp + json.dumps(payload)
    signature = hmac.new(
        bytearray.fromhex(signature_key), data.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(close_sig_hash, signature)
