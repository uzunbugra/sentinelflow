#!/usr/bin/env python
"""
Database Seeder & Real Data Simulator

Simulates real-world bank data based on the structure of the PaySim dataset.
Instead of sending sensitive information, it acts like a bank's on-premise
agent: it only sends what is necessary and sends it to our new Ingestor API.
"""

import asyncio
import httpx
import random
import time
from datetime import datetime, timezone
import string

API_URL = "http://localhost:8000/api/v1/ingest/transaction"

def generate_random_iban():
    """Generate a valid looking TR IBAN."""
    bank_code = "00061" # Vakıfbank for example
    account = ''.join(random.choices(string.digits, k=16))
    return f"TR33{bank_code}0{account}"

async def simulate_traffic(num_transactions: int = 100, delay_ms: float = 100.0):
    """
    Generate and push realistic transactions to the Ingest endpoint.
    Includes normal traffic and occasional ML-triggering anomalies.
    """
    print(f"Starting real data simulation: {num_transactions} txs to {API_URL}")
    
    # Store some ibans to create graphs/rings later if needed
    known_ibans = [generate_random_iban() for _ in range(50)]
    
    async with httpx.AsyncClient() as client:
        for i in range(num_transactions):
            # 5% chance of being an anomaly (very high amount)
            is_anomaly = random.random() < 0.05
            
            amount = round(random.uniform(10.0, 5000.0), 2)
            if is_anomaly:
                amount = round(random.uniform(50000.0, 500000.0), 2)
            
            # Select sender and receiver
            sender = random.choice(known_ibans)
            receiver = random.choice(known_ibans)
            while receiver == sender:
                receiver = random.choice(known_ibans)
                
            payload = {
                "sender_iban": sender,
                # Notice we do NOT send names or descriptions, simulating strict bank privacy
                "receiver_iban": receiver,
                "amount": amount,
                "currency": "TRY",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "channel": random.choice(["api", "mobile", "web"])
            }
            
            try:
                resp = await client.post(API_URL, json=payload)
                if resp.status_code == 202:
                    print(f"[{i+1}/{num_transactions}] Ingested: {amount} TRY from {sender[:8]}... -> {resp.json().get('status')}")
                else:
                    print(f"[{i+1}/{num_transactions}] Failed: {resp.status_code} - {resp.text}")
            except Exception as e:
                print(f"[{i+1}/{num_transactions}] Connection Error: {e}")
                
            await asyncio.sleep(delay_ms / 1000.0)

if __name__ == "__main__":
    asyncio.run(simulate_traffic(num_transactions=500, delay_ms=50))
