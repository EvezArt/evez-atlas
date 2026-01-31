# Hermetic Console Run Steps

1. Deploy all services:
   ```sh
   ./scripts/deploy-all.sh
   ```
2. Start the monitoring server:
   ```sh
   python tools/monitor_server.py --port 8001
   ```
3. Open port 8001 in your environment.
4. Run the audit analyzer:
   ```sh
   python tools/audit_analyzer.py --api-key tier3_director --api-base http://localhost:8000
   ```
