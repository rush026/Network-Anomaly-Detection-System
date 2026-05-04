# ─────────────────────────────────────────────────────────────
# Makefile — Network Anomaly Detection convenience commands
# ─────────────────────────────────────────────────────────────
PROJECT_DIR := $(shell pwd)
API_ENV     := $(PROJECT_DIR)/api_env
ML_ENV      := $(PROJECT_DIR)/ml_env

.PHONY: deploy stop api dashboard train preprocess evaluate help

## deploy : Start both FastAPI API + Streamlit dashboard
deploy:
	@chmod +x deploy.sh
	@./deploy.sh

## stop : Stop all running services
stop:
	@./deploy.sh --stop

## api : Start only the FastAPI backend (port 8000)
api:
	@echo "Starting FastAPI on http://localhost:8000 ..."
	@mkdir -p logs
	@$(API_ENV)/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

## dashboard : Start only the Streamlit dashboard (port 8501)
dashboard:
	@echo "Starting Streamlit dashboard on http://localhost:8501 ..."
	@$(API_ENV)/bin/streamlit run dashboard/app.py --server.port 8501

## preprocess : Run data preprocessing (uses ml_env)
preprocess:
	@echo "Running preprocessing..."
	@$(ML_ENV)/bin/python training/preprocess.py

## train : Train all three models (uses ml_env)
train:
	@echo "Training XGBoost..."
	@$(ML_ENV)/bin/python training/train_xgb.py
	@echo "Training Isolation Forest..."
	@$(ML_ENV)/bin/python training/train_iso.py
	@echo "Training Autoencoder..."
	@$(ML_ENV)/bin/python training/train_autoencoder.py
	@echo "All models trained ✅"

## evaluate : Evaluate model performance (uses ml_env)
evaluate:
	@echo "Running evaluation..."
	@$(ML_ENV)/bin/python training/evaluate.py

## predict : Run a quick test prediction via curl
predict:
	@curl -s -X POST http://localhost:8000/predict \
		-H "Content-Type: application/json" \
		-d '{"Flow_Duration":1000,"Total_Fwd_Packets":10,"Total_Backward_Packets":5,"Total_Length_of_Fwd_Packets":500}' \
		| python3 -m json.tool

## logs-api : Tail the API server log
logs-api:
	@tail -f logs/api.log

## logs-dash : Tail the dashboard log
logs-dash:
	@tail -f logs/dashboard.log

## help : Show this help message
help:
	@echo ""
	@echo "Network Anomaly Detection — Available commands:"
	@echo ""
	@grep -E '^## ' Makefile | sed 's/## /  make /' | column -t -s ':'
	@echo ""
