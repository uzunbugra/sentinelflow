"""
Data Privacy and Anonymization Module.
Provides one-way hashing and tokenization for sensitive PII (Personally Identifiable Information).
Used by ingestors to ensure no cleartext banking data enters the detection stream.
"""

import hashlib
import hmac
import os
from typing import Optional

# Secret key for HMAC-based tokenization. In production, load from environment.
_SECRET_KEY = os.getenv("ANONYMIZER_SECRET_KEY", "default-secret-key-sentinelflow-2026").encode("utf-8")

def anonymize_iban(iban: str) -> str:
    """
    Anonymize IBAN using HMAC-SHA256.
    Returns a consistent tokenized string so graph algorithms (Neo4j) still work,
    but the original IBAN cannot be reversed.
    Example output format: TR_HASH1234567890abcdef
    """
    if not iban:
        return ""
    
    # Clean IBAN
    clean_iban = iban.strip().upper().replace(" ", "")
    
    # Create HMAC
    h = hmac.new(_SECRET_KEY, clean_iban.encode("utf-8"), hashlib.sha256)
    hashed_val = h.hexdigest()[:16] # Take first 16 chars for manageable length
    
    # Preserve country code if it exists (first 2 chars) for logic that might need it
    prefix = clean_iban[:2] if len(clean_iban) >= 2 and clean_iban[:2].isalpha() else "XX"
    
    return f"{prefix}_{hashed_val}"

def anonymize_string(text: Optional[str]) -> Optional[str]:
    """
    Anonymize any string (names, descriptions) into a hash.
    Returns None if input is None.
    """
    if not text:
        return None
        
    h = hmac.new(_SECRET_KEY, text.encode("utf-8"), hashlib.sha256)
    return h.hexdigest()

def mask_string(text: Optional[str], show_last: int = 4) -> Optional[str]:
    """
    Mask a string showing only the last N characters.
    Useful for displaying safe fragments on dashboards.
    """
    if not text:
        return None
    
    if len(text) <= show_last:
        return "*" * len(text)
        
    return "*" * (len(text) - show_last) + text[-show_last:]
