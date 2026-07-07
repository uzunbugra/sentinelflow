@echo off
echo Starting SentinelFlow FULL SYSTEM (Big Data Mode)...

:: 1. Start Backend (API + WebSocket)
echo Launching Backend...
start "SentinelFlow Backend" cmd /k "set PYTHONPATH=%CD%\src && .\.venv\Scripts\python.exe -m sentinelflow.api.app"

:: 2. Start Kafka Ingestor (Bridge)
echo Launching Ingestor...
start "SentinelFlow Kafka Ingestor" cmd /k "set PYTHONPATH=%CD%\src && .\.venv\Scripts\python.exe src\sentinelflow\ingestor\kafka_consumer.py --kafka-servers localhost:9092 --topic transactions"

:: 3. Start Real Data Simulator (Bank API Client)
echo Launching Real Data Simulator...
start "SentinelFlow Bank API Client" cmd /k "set PYTHONPATH=%CD%\src && .\.venv\Scripts\python.exe scripts\import_real_test_data.py"

:: 4. Start Frontend (Next.js)
echo Launching Frontend...
cd sentinelflow-web
start "SentinelFlow Dashboard" cmd /k "npm run dev"

echo ===================================================
echo SYSTEM LAUNCHED! 🚀
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo Data Flow: Generator -> Kafka -> Ingestor -> API
echo ===================================================
pause
