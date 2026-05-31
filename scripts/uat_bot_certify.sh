#!/usr/bin/env bash
set -euo pipefail

# Industrial UAT bot-trading certification runner.
#
# What it does:
# 1) Preflight checks (deployed SHA, service health, endpoint reachability)
# 2) Creates an ephemeral bot key in trading_uat
# 3) Runs full bot E2E suite N consecutive times (default: 3)
# 4) Writes JUnit artifacts per run
# 5) Cleans up ephemeral bot key even on failure
#
# Usage:
#   scripts/uat_bot_certify.sh
#   scripts/uat_bot_certify.sh --runs 3 --report-dir reports/uat-cert

RUNS=3
REPORT_DIR="reports/uat-cert"
UAT_HOST="145.241.243.140"
SSH_KEY="${HOME}/.oci/vm_ssh_key"
UAT_BASE="https://uat.vectrade.io/api/trade/v1/bot"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --runs)
      RUNS="$2"
      shift 2
      ;;
    --report-dir)
      REPORT_DIR="$2"
      shift 2
      ;;
    --host)
      UAT_HOST="$2"
      shift 2
      ;;
    --ssh-key)
      SSH_KEY="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1"
      exit 2
      ;;
  esac
done

if ! [[ "$RUNS" =~ ^[0-9]+$ ]] || [[ "$RUNS" -lt 1 ]]; then
  echo "--runs must be a positive integer"
  exit 2
fi

if [[ ! -f "$SSH_KEY" ]]; then
  echo "SSH key not found: $SSH_KEY"
  exit 2
fi

mkdir -p "$REPORT_DIR"
TS="$(date +%Y%m%d-%H%M%S)"
SUMMARY_FILE="$REPORT_DIR/summary-$TS.txt"

BOT_KEY=""
BOT_KEY_HASH=""

log() {
  printf '[%s] %s\n' "$(date +%H:%M:%S)" "$*"
}

ssh_uat() {
  ssh -i "$SSH_KEY" "ubuntu@$UAT_HOST" "$@"
}

cleanup_key() {
  if [[ -z "$BOT_KEY_HASH" ]]; then
    return 0
  fi
  log "Cleaning up ephemeral bot key"
  cat <<PY | ssh_uat "sudo -u finance /opt/finance/app-uat/.venv/bin/python3 -" >/dev/null
import re
import subprocess
from pathlib import Path

env_text = Path('/opt/finance/env/.env.uat').read_text()
match = re.search(r'^TRADING_DATABASE_URL=(.+)$', env_text, re.MULTILINE)
if not match:
    raise SystemExit(0)

db_url = match.group(1).replace('postgresql+asyncpg://', 'postgresql://').replace('?ssl=disable', '')
key_hash = "${BOT_KEY_HASH}".strip()
if not key_hash:
    raise SystemExit(0)

sql = f"DELETE FROM bot_api_keys WHERE key_hash = '{key_hash}'"
subprocess.run(['psql', db_url, '-v', 'ON_ERROR_STOP=1', '-c', sql], check=False, stdout=subprocess.DEVNULL)
PY
}

trap cleanup_key EXIT

create_ephemeral_key() {
  log "Creating ephemeral bot key"
  local key_output
  key_output="$(cat <<'PY' | ssh_uat "sudo -u finance /opt/finance/app-uat/.venv/bin/python3 -"
import hashlib
import re
import secrets
import subprocess
import uuid
from pathlib import Path

env_text = Path('/opt/finance/env/.env.uat').read_text()
match = re.search(r'^TRADING_DATABASE_URL=(.+)$', env_text, re.MULTILINE)
if not match:
    raise SystemExit('TRADING_DATABASE_URL not found')

db_url = match.group(1).replace('postgresql+asyncpg://', 'postgresql://').replace('?ssl=disable', '')

key = 'tvt_' + secrets.token_urlsafe(32)
key_hash = hashlib.sha256(key.encode()).hexdigest()
key_prefix = key[:8]
user_id = subprocess.check_output(
    ['psql', db_url, '-Atc', "SELECT id FROM users WHERE is_active = true ORDER BY random() LIMIT 1"],
    text=True,
).strip()
if not user_id:
    raise SystemExit('No active user found')

key_id = str(uuid.uuid4())
sql = (
    "INSERT INTO bot_api_keys (id, user_id, key_hash, key_prefix, label, is_active, created_at) "
    f"VALUES ('{key_id}', '{user_id}', '{key_hash}', '{key_prefix}', 'UAT INDUSTRIAL CERT', true, now())"
)
subprocess.check_call(['psql', db_url, '-v', 'ON_ERROR_STOP=1', '-c', sql], stdout=subprocess.DEVNULL)

print(f'BOT_KEY={key}')
print(f'BOT_KEY_HASH={key_hash}')
print(f'BOT_KEY_PREFIX={key_prefix}')
print(f'BOT_USER_ID={user_id}')
PY
)"

  BOT_KEY="$(printf '%s\n' "$key_output" | awk -F= '/^BOT_KEY=/{print $2}')"
  BOT_KEY_HASH="$(printf '%s\n' "$key_output" | awk -F= '/^BOT_KEY_HASH=/{print $2}')"
  BOT_KEY_PREFIX="$(printf '%s\n' "$key_output" | awk -F= '/^BOT_KEY_PREFIX=/{print $2}')"
  BOT_USER_ID="$(printf '%s\n' "$key_output" | awk -F= '/^BOT_USER_ID=/{print $2}')"

  if [[ -z "$BOT_KEY" || -z "$BOT_KEY_HASH" ]]; then
    echo "ERROR: failed to create ephemeral bot key"
    printf '%s\n' "$key_output"
    exit 1
  fi

  log "Ephemeral key created (prefix=$BOT_KEY_PREFIX user_id=$BOT_USER_ID)"
}

log "Starting UAT bot certification"
{
  echo "certification_timestamp=$TS"
  echo "runs=$RUNS"
  echo "uat_host=$UAT_HOST"
  echo "uat_base=$UAT_BASE"
} > "$SUMMARY_FILE"

log "Preflight: deployed SHA"
DEPLOYED_SHA="$(ssh_uat "sudo -u finance bash -lc 'cd /opt/finance/app-uat && git rev-parse --short HEAD'")"
log "UAT deployed SHA: $DEPLOYED_SHA"
echo "deployed_sha=$DEPLOYED_SHA" >> "$SUMMARY_FILE"

log "Preflight: service health"
SERVICE_STATUS="$(ssh_uat "systemctl is-active finance-site@uat finance-api@uat finance-collector@uat finance-trading@uat")"
echo "$SERVICE_STATUS" | awk '{print "service_status=" $0}' >> "$SUMMARY_FILE"
if echo "$SERVICE_STATUS" | grep -qv '^active$'; then
  echo "ERROR: one or more UAT services are not active"
  echo "$SERVICE_STATUS"
  exit 1
fi

log "Preflight: endpoint reachability"
curl -fsS "https://uat.vectrade.io" >/dev/null
curl -fsS "https://analytics.vectrade.io/api/heartbeat" >/dev/null

PASS_COUNT=0
for i in $(seq 1 "$RUNS"); do
  create_ephemeral_key

  {
    echo "run_${i}_bot_key_prefix=$BOT_KEY_PREFIX"
    echo "run_${i}_bot_user_id=$BOT_USER_ID"
  } >> "$SUMMARY_FILE"

  log "Run $i/$RUNS: authenticated smoke checks"
  curl -fsS "$UAT_BASE/account" -H "X-Bot-Key: $BOT_KEY" >/dev/null
  curl -fsS "$UAT_BASE/kpi" -H "X-Bot-Key: $BOT_KEY" >/dev/null

  RUN_XML="$REPORT_DIR/uat-bot-e2e-$TS-run$i.xml"
  RUN_LOG="$REPORT_DIR/uat-bot-e2e-$TS-run$i.log"
  log "Run $i/$RUNS: full E2E suite"
  set +e
  VECTRADE_BOT_KEY="$BOT_KEY" VECTRADE_BOT_API_BASE="$UAT_BASE" \
    pytest tests/test_bot_e2e.py -v --durations=10 --junitxml="$RUN_XML" | tee "$RUN_LOG"
  EXIT_CODE=${PIPESTATUS[0]}
  set -e

  echo "run_${i}_exit_code=$EXIT_CODE" >> "$SUMMARY_FILE"
  echo "run_${i}_xml=$RUN_XML" >> "$SUMMARY_FILE"

  if [[ "$EXIT_CODE" -ne 0 ]]; then
    log "Run $i failed"
    echo "overall_result=FAILED" >> "$SUMMARY_FILE"
    echo "failed_run=$i" >> "$SUMMARY_FILE"
    exit "$EXIT_CODE"
  fi

  cleanup_key
  BOT_KEY=""
  BOT_KEY_HASH=""

  PASS_COUNT=$((PASS_COUNT + 1))
  log "Run $i passed"
done

log "All runs passed ($PASS_COUNT/$RUNS)"
{
  echo "overall_result=PASSED"
  echo "passed_runs=$PASS_COUNT"
} >> "$SUMMARY_FILE"

log "Certification summary: $SUMMARY_FILE"
cat "$SUMMARY_FILE"
