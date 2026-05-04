---
description: Deploy the Network Anomaly Detection project
---

## Steps to Deploy

1. **Ensure environment is set up**
   - Verify that the virtual environment `api_env` exists in the project root.
   - If not, create it: `python -m venv api_env && source api_env/bin/activate && pip install -r requirements.txt`

2. **Run the deployment script**
   // turbo
   ```bash
   ./deploy.sh
   ```

3. **Verify services**
   - Open a browser and navigate to `http://localhost:8000/docs` to check the FastAPI docs.
   - Open `http://localhost:8501` to view the Streamlit dashboard.

4. **Stop services when done**
   ```bash
   ./deploy.sh --stop
   ```

## Notes
- The script will automatically kill any processes using the required ports before starting.
- Logs are written to `logs/api.log` and `logs/dashboard.log`.
- Ensure trained model files exist in `models/` before deploying.
