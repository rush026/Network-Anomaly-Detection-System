#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# deploy.sh  –  Starts the FastAPI backend + Streamlit dashboard
# Usage: ./deploy.sh
#        ./deploy.sh --stop
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_ENV="$PROJECT_DIR/api_env"
API_PID_FILE="$PROJECT_DIR/.api.pid"
DASH_PID_FILE="$PROJECT_DIR/.dash.pid"
API_PORT=8000
DASH_PORT=8501
API_LOG="$PROJECT_DIR/logs/api.log"
DASH_LOG="$PROJECT_DIR/logs/dashboard.log"

# ── Colours ───────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; BOLD='\033[1m'; RESET='\033[0m'

banner() {
  echo -e "${BOLD}${BLUE}"
  echo "╔══════════════════════════════════════════════════╗"
  echo "║   Network Anomaly Detection — Deploy Script      ║"
  echo "╚══════════════════════════════════════════════════╝"
  echo -e "${RESET}"
}

log_info()  { echo -e "${GREEN}[✔]${RESET} $*"; }
log_warn()  { echo -e "${YELLOW}[!]${RESET} $*"; }
log_error() { echo -e "${RED}[✘]${RESET} $*"; }

# ── Stop helper ───────────────────────────────────────────────
stop_services() {
  echo -e "${BOLD}Stopping services...${RESET}"
  for PFILE in "$API_PID_FILE" "$DASH_PID_FILE"; do
    if [[ -f "$PFILE" ]]; then
      PID=$(cat "$PFILE")
      if kill -0 "$PID" 2>/dev/null; then
        kill "$PID" && log_info "Stopped process $PID"
      fi
      rm -f "$PFILE"
    fi
  done
  log_info "All services stopped."
}

# ── Handle --stop flag ────────────────────────────────────────
if [[ "${1:-}" == "--stop" ]]; then
  stop_services
  exit 0
fi

banner

# ── Sanity checks ─────────────────────────────────────────────
if [[ ! -d "$API_ENV" ]]; then
  log_error "api_env not found at $API_ENV"
  exit 1
fi

if [[ ! -f "$PROJECT_DIR/models/xgb_model.pkl" ]] && [[ ! -f "$PROJECT_DIR/models/xgb_model.json" ]]; then
  log_error "XGBoost model not found in models/."
  exit 1
fi

if [[ ! -f "$PROJECT_DIR/models/iso_model.pkl" ]] || \
   [[ ! -f "$PROJECT_DIR/models/autoencoder.h5" ]] || \
   [[ ! -f "$PROJECT_DIR/models/scaler.pkl" ]]; then
  log_error "Trained models (Isolation Forest or Autoencoder or Scaler) not found in models/. Run training first:"
  echo "       make train   (or see README.md)"
  exit 1
fi

mkdir -p "$PROJECT_DIR/logs"

# ── Kill any stale services on those ports ────────────────────
for PORT in $API_PORT $DASH_PORT; do
  EXISTING=$(lsof -ti tcp:"$PORT" 2>/dev/null || true)
  if [[ -n "$EXISTING" ]]; then
    log_warn "Port $PORT in use by PID $EXISTING — killing..."
    kill -9 "$EXISTING" 2>/dev/null || true
  fi
done
# Final check for uvicorn/streamlit by name
pkill -f "uvicorn backend.main:app" || true
pkill -f "streamlit run .*dashboard/app.py" || true
sleep 2

# ── Start FastAPI backend ─────────────────────────────────────
log_info "Starting FastAPI backend on http://localhost:${API_PORT} ..."
cd "$PROJECT_DIR"
"$API_ENV/bin/uvicorn" backend.main:app \
  --host 0.0.0.0 \
  --port "$API_PORT" \
  --log-level info \
  >"$API_LOG" 2>&1 &
API_PID=$!
echo "$API_PID" > "$API_PID_FILE"
log_info "FastAPI PID: $API_PID  (log → logs/api.log)"

# ── Wait for API to be healthy ────────────────────────────────
echo -ne "${YELLOW}Waiting for API to start${RESET}"
MAX_WAIT=45
COUNT=0
until curl -sf "http://localhost:${API_PORT}/" >/dev/null 2>&1; do
  sleep 1
  echo -n "."
  ((COUNT++))
  if [[ $COUNT -ge $MAX_WAIT ]]; then
    echo ""
    log_error "API did not start within ${MAX_WAIT}s. Check logs/api.log"
    exit 1
  fi
done
echo ""
log_info "API is healthy ✅  →  http://localhost:${API_PORT}"

# ── Start Streamlit dashboard ─────────────────────────────────
log_info "Starting Streamlit dashboard on http://localhost:${DASH_PORT} ..."
"$API_ENV/bin/streamlit" run "$PROJECT_DIR/dashboard/app.py" \
  --server.port "$DASH_PORT" \
  --server.headless true \
  >"$DASH_LOG" 2>&1 &
DASH_PID=$!
echo "$DASH_PID" > "$DASH_PID_FILE"
log_info "Streamlit PID: $DASH_PID  (log → logs/dashboard.log)"

sleep 2

# ── Summary ───────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}═══════════════════════════════════════════════${RESET}"
echo -e "${BOLD}  🚀 Deployment complete!${RESET}"
echo -e "${GREEN}  API      →  http://localhost:${API_PORT}${RESET}"
echo -e "${GREEN}  API Docs →  http://localhost:${API_PORT}/docs${RESET}"
echo -e "${GREEN}  Dashboard→  http://localhost:${DASH_PORT}${RESET}"
echo -e "${BOLD}${GREEN}═══════════════════════════════════════════════${RESET}"
echo ""
echo -e "  To stop all services:  ${YELLOW}./deploy.sh --stop${RESET}  or  ${YELLOW}make stop${RESET}"
echo ""
