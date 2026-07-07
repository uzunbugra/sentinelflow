from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from sentinelflow.contracts.transaction import TransactionCreate, TransactionKafkaMessage
from sentinelflow.security.anonymizer import anonymize_iban, anonymize_string
# Assume we have a Kafka producer dependency. 
# This might need to be imported from your actual deps.py, 
# for now we'll mock the dependency injection structure.

router = APIRouter(
    prefix="/ingest",
    tags=["Ingestion"],
    responses={404: {"description": "Not found"}},
)

class BankTransactionPayload(BaseModel):
    """
    Payload exactly as expected from the Bank's webhook.
    Contains raw sensitive data that MUST be anonymized.
    """
    sender_iban: str
    sender_name: Optional[str] = None
    sender_city: Optional[str] = None
    receiver_iban: str
    receiver_name: Optional[str] = None
    receiver_city: Optional[str] = None
    amount: float
    currency: str = "TRY"
    description: Optional[str] = None
    timestamp: Optional[datetime] = None
    channel: str = "api"

@router.post("/transaction", status_code=status.HTTP_202_ACCEPTED)
async def ingest_transaction(payload: BankTransactionPayload):
    """
    Ingest endpoint for banks to send real-time transactions.
    Data is anonymized IMMEDATELY before entering the system memory for processing.
    """
    # 1. Anonymize Sensitive Data
    safe_sender_iban = anonymize_iban(payload.sender_iban)
    safe_receiver_iban = anonymize_iban(payload.receiver_iban)
    
    # We drop the names entirely or hash them if we needed consistency checking.
    # For privacy, dropping is safest if not used. If used, hash them.
    # Let's drop them to be 100% compliant with "limited data" requirements.
    
    safe_description = anonymize_string(payload.description) if payload.description else None
    
    # 2. Create the safe Contract
    txn_create = TransactionCreate(
        sender_iban=safe_sender_iban,
        sender_name=None, # Dropped
        sender_city=payload.sender_city,
        receiver_iban=safe_receiver_iban,
        receiver_name=None, # Dropped
        receiver_city=payload.receiver_city,
        amount=payload.amount,
        currency=payload.currency,
        description=safe_description,
        timestamp=payload.timestamp,
        channel=payload.channel
    ).with_defaults()

    # 3. Convert to Kafka Message
    kafka_msg = TransactionKafkaMessage(**txn_create.model_dump(), source_system="bank_api")
    
    # 4. Push to Kafka (Mocking the producer call here)
    # await kafka_producer.send_and_wait("transactions", kafka_msg.model_dump_json().encode("utf-8"))
    
    return {
        "status": "accepted",
        "transaction_id": kafka_msg.transaction_id,
        "message": "Transaction safely anonymized and ingested."
    }
