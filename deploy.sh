#!/usr/bin/env bash
set -euo pipefail

# deploy.sh - простой скрипт деплоя для виртуальной машины
# Usage: ./deploy.sh [branch]
# Пример: ./deploy.sh main

BRANCH=${1:-main}
REPO_DIR="${HOME}/moex_trading_bot"
VENV_DIR="${REPO_DIR}/venv"

echo "Deploying branch ${BRANCH} to ${REPO_DIR}"

if [ ! -d "${REPO_DIR}" ]; then
  echo "ERROR: repository directory ${REPO_DIR} not found"
  exit 1
fi

cd "${REPO_DIR}"

echo "Fetching latest..."
git fetch origin
git checkout "${BRANCH}" || git switch "${BRANCH}"
git pull origin "${BRANCH}"

echo "Ensure logs directories exist"
mkdir -p logs/trading logs/errors logs/performance

if [ -f "${VENV_DIR}/bin/activate" ]; then
  echo "Activating venv"
  # shellcheck source=/dev/null
  source "${VENV_DIR}/bin/activate"
else
  echo "Creating venv at ${VENV_DIR}"
  python3 -m venv "${VENV_DIR}"
  # shellcheck source=/dev/null
  source "${VENV_DIR}/bin/activate"
fi

echo "Installing requirements"
pip install --upgrade pip
pip install -r requirements.txt

echo "Stopping running bot (if any)"
pkill -f main.py || true

echo "Starting bot"
nohup python main.py &> logs/trading/bot.log &

PID=$(pgrep -f main.py || true)
echo "Started bot, PID: ${PID}"

echo "Deploy finished"
