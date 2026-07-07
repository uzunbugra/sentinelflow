@echo off
echo ===================================================
echo SentinelFlow - Enterprise Production Launch
echo ===================================================
echo This will build and launch all services in Docker.
echo Including: API, Ingestor, Frontend, Kafka, Postgres, Neo4j, Redis

docker compose up -d --build

echo ===================================================
echo SYSTEM LAUNCHED! 🚀
echo Backend API: http://localhost:8000
echo Frontend Dashboard: http://localhost:3000
echo Kafka UI: http://localhost:8080
echo Neo4j Browser: http://localhost:7474
echo Redis Commander: http://localhost:8081
echo ===================================================
echo To view logs, run: docker compose logs -f
pause
