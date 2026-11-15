#!/usr/bin/env bash
# End-to-end smoke test: build and start the real stack (web + api + postgres)
# under a throwaway compose project, hit it with curl, always tear it down.
set -euo pipefail

cd "$(dirname "$0")/.."

PROJECT="splitbill-smoke-$$"
API_PORT="${SMOKE_API_PORT:-28000}"
WEB_PORT="${SMOKE_WEB_PORT:-25173}"
API="http://localhost:${API_PORT}"
WEB="http://localhost:${WEB_PORT}"
KEY="smoke-key-$$"
OWNER="11111111-1111-4111-8111-111111111111"
OTHER="22222222-2222-4222-8222-222222222222"

ENV_FILE="$(mktemp)"
BODY_FILE="$(mktemp)"
cat > "$ENV_FILE" <<ENV
API_KEY=${KEY}
POSTGRES_USER=smoke
POSTGRES_PASSWORD=smoke
POSTGRES_DB=smoke
DATABASE_URL=postgresql+asyncpg://smoke:smoke@postgres:5432/smoke
OPENROUTER_API_KEY=dummy
CONTAINER_PREFIX=${PROJECT}
API_IMAGE=${PROJECT}-api
WEB_IMAGE=${PROJECT}-web
API_PORT=${API_PORT}
WEB_PORT=${WEB_PORT}
POSTGRES_PORT=${SMOKE_POSTGRES_PORT:-25432}
VITE_FASTAPI_API_URL=${API}
APP_BASE_URL=${WEB}
ENV

COMPOSE=(docker compose -p "$PROJECT" --env-file "$ENV_FILE" -f docker/docker-compose.yml)

teardown() {
  echo "== teardown"
  "${COMPOSE[@]}" down -v --remove-orphans || true
  docker image rm "${PROJECT}-api" "${PROJECT}-web" >/dev/null 2>&1 || true
  rm -f "$ENV_FILE" "$BODY_FILE"
}
trap teardown EXIT

fail() { echo "FAIL: $*" >&2; exit 1; }
pass() { echo "ok   $*"; }

# status CODE METHOD URL [curl args...]: body goes to $BODY
status() {
  local want="$1" method="$2" url="$3"; shift 3
  local got
  got=$(curl -s -o "$BODY_FILE" -w '%{http_code}' -X "$method" "$url" "$@")
  BODY=$(cat "$BODY_FILE")
  [ "$got" = "$want" ] || fail "$method $url: want $want, got $got: $BODY"
  pass "$method $url -> $got"
}

echo "== build and start ($PROJECT)"
"${COMPOSE[@]}" up -d --build

echo "== wait for health"
for _ in $(seq 1 60); do
  curl -sf "$API/health/" >/dev/null && curl -sf "$WEB/" >/dev/null && break
  sleep 2
done

AUTH=(-H "Authorization: Bearer ${KEY}")
JSON=(-H "Content-Type: application/json")

status 200 GET "$API/health/"

status 200 POST "$API/splits/calculate" "${AUTH[@]}" "${JSON[@]}" -H "X-Device-Id: $OWNER" \
  -d '{"person_names":["Alice","Bob"],"client_results":{"Alice":{"total":12.5},"Bob":{"total":7.5}}}'
ID=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["split_id"])' "$BODY")

status 200 GET "$API/splits/view/$ID"
python3 -c 'import json,sys; r=json.loads(sys.argv[1])["calculated_split_results"]; assert r["Alice"]["total"]==12.5 and r["Bob"]["total"]==7.5, r' "$BODY" \
  || fail "view totals do not match"
pass "view totals match"

status 200 PUT "$API/splits/$ID/payments/Alice" "${AUTH[@]}" "${JSON[@]}" -H "X-Device-Id: $OWNER" -d '{"paid":true}'
status 200 GET "$API/splits/view/$ID"
python3 -c 'import json,sys; assert json.loads(sys.argv[1])["payments"]=={"Alice":"paid"}' "$BODY" \
  || fail "view does not show Alice paid: $BODY"
pass "view shows Alice paid"

status 404 PUT "$API/splits/$ID/payments/Alice" "${AUTH[@]}" "${JSON[@]}" -H "X-Device-Id: $OTHER" -d '{"paid":false}'
status 401 GET "$API/groups/" "${AUTH[@]}"

status 200 GET "$WEB/"
grep -q '<div' <<<"$BODY" && grep -q '_app/' <<<"$BODY" || fail "web root is not the app shell"
pass "web root contains the app shell"
status 200 GET "$WEB/split/$ID"

echo "== all smoke checks passed"
