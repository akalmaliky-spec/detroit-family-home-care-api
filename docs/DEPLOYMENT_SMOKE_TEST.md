# DFHC API Post-Deploy Smoke Test

Use this checklist immediately after deploying the API to Render or Railway.

## 1. Health endpoint

curl https://YOUR-API-DOMAIN/health

Expected:
{"status":"ok","service":"dfhc-api"}

## 2. API docs

Open:
https://YOUR-API-DOMAIN/docs

## 3. Auth flow

POST /users/
POST /auth/token

## 4. Clients auth gate

401 without token
200 with token

## 5. Create client

POST /clients/

## 6. Failure conditions

Stop if anything fails
