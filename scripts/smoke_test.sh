#!/usr/bin/env bash
set -euo pipefail
set +x

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 https://your-api-domain"
  exit 1
fi
BASE_URL="${1%/}"
[[ "$BASE_URL" == https://* || "$BASE_URL" == http://127.0.0.1:* || "$BASE_URL" == http://localhost:* ]] || { echo "Use HTTPS or loopback"; exit 1; }
command -v curl >/dev/null || { echo "curl is required"; exit 1; }

expect_status() {
  local expected="$1" path="$2" status
  status=$(curl --connect-timeout 10 --max-time 30 -sS -o /dev/null -w "%{http_code}" "$BASE_URL$path")
  [[ "$status" == "$expected" ]] || { echo "$path: expected $expected, got $status"; exit 1; }
}
expect_status 200 /health
expect_status 401 /users/
expect_status 401 /clients/

if [[ -n "${DFHC_SMOKE_ACCESS_TOKEN:-}" ]]; then
  case "${DFHC_SMOKE_ROLE:-member}" in
    member) USER_STATUS=403 ;;
    admin) USER_STATUS=200 ;;
    *) echo "DFHC_SMOKE_ROLE must be member or admin"; exit 1 ;;
  esac
  umask 077
  HEADER_FILE=$(mktemp)
  trap 'rm -f "$HEADER_FILE"' EXIT
  printf 'Authorization: Bearer %s\n' "$DFHC_SMOKE_ACCESS_TOKEN" > "$HEADER_FILE"
  for path in /users/me /clients/ /users/; do
    expected=200
    [[ "$path" != /users/ ]] || expected="$USER_STATUS"
    status=$(curl --connect-timeout 10 --max-time 30 -sS -o /dev/null -w "%{http_code}" -H "@$HEADER_FILE" "$BASE_URL$path")
    [[ "$status" == "$expected" ]] || { echo "$path: expected $expected, got $status"; exit 1; }
  done
fi
echo "Read-only smoke checks passed. Complete staging refresh/revocation and ownership checks before rollout."
