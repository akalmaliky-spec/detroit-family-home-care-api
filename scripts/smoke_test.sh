#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 https://your-api-domain"
  exit 1
fi

BASE_URL="${1%/}"
EMAIL="admin@dfhc.test"
PASSWORD="StrongPass123"

command -v curl >/dev/null 2>&1 || { echo "curl is required"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "python3 is required"; exit 1; }

extract_json_field() {
  python3 -c 'import json,sys; print(json.load(sys.stdin).get(sys.argv[1], ""))' "$1"
}

echo "[1/5] Checking /health"
HEALTH_RESPONSE=$(curl -fsS "$BASE_URL/health")
echo "$HEALTH_RESPONSE"

echo "[2/5] Creating smoke-test user (201 or 400 are acceptable)"
CREATE_STATUS=$(curl -sS -o /tmp/dfhc_create_user.json -w "%{http_code}" \
  -X POST "$BASE_URL/users/" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\",\"full_name\":\"DFHC Admin\",\"is_active\":true}")
if [[ "$CREATE_STATUS" != "201" && "$CREATE_STATUS" != "400" ]]; then
  echo "Unexpected /users/ status: $CREATE_STATUS"
  cat /tmp/dfhc_create_user.json
  exit 1
fi

echo "[3/5] Fetching auth token"
TOKEN_RESPONSE=$(curl -fsS \
  -X POST "$BASE_URL/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$EMAIL&password=$PASSWORD")
TOKEN=$(printf '%s' "$TOKEN_RESPONSE" | extract_json_field access_token)
if [[ -z "$TOKEN" ]]; then
  echo "No access token returned"
  echo "$TOKEN_RESPONSE"
  exit 1
fi

echo "[4/5] Verifying /clients auth gate"
NO_AUTH_STATUS=$(curl -sS -o /tmp/dfhc_clients_noauth.json -w "%{http_code}" "$BASE_URL/clients/")
if [[ "$NO_AUTH_STATUS" != "401" ]]; then
  echo "Expected 401 without token, got: $NO_AUTH_STATUS"
  cat /tmp/dfhc_clients_noauth.json
  exit 1
fi

WITH_AUTH_STATUS=$(curl -sS -o /tmp/dfhc_clients_auth.json -w "%{http_code}" \
  "$BASE_URL/clients/" \
  -H "Authorization: Bearer $TOKEN")
if [[ "$WITH_AUTH_STATUS" != "200" ]]; then
  echo "Expected 200 with token, got: $WITH_AUTH_STATUS"
  cat /tmp/dfhc_clients_auth.json
  exit 1
fi

echo "[5/5] Creating a smoke-test client"
CLIENT_STATUS=$(curl -sS -o /tmp/dfhc_create_client.json -w "%{http_code}" \
  -X POST "$BASE_URL/clients/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"full_name":"Mary Johnson","date_of_birth":"1980-05-15","diagnosis":"Cerebral Palsy","address":"123 Main St, Detroit, MI 48201","phone":"313-555-1234","emergency_contact_name":"James Johnson","emergency_contact_phone":"313-555-5678","medicaid_id":"MI12345678","is_active":true,"notes":"Requires wheelchair access"}')
if [[ "$CLIENT_STATUS" != "201" ]]; then
  echo "Expected 201 from /clients/, got: $CLIENT_STATUS"
  cat /tmp/dfhc_create_client.json
  exit 1
fi

echo "Smoke test passed for $BASE_URL"
