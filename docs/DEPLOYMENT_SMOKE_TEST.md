# DFHC API Post-Deploy Smoke Test

Use this checklist immediately after deploying the API to Render or Railway.

## 1. Health endpoint

Request:

```bash
curl https://YOUR-API-DOMAIN/health
```

Expected response:

```json
{"status":"ok","service":"dfhc-api"}
```

## 2. API docs

Open:

- `https://YOUR-API-DOMAIN/docs`

Expected result:

- Swagger UI loads
- `/health`, `/auth/token`, `/users`, and `/clients` routes are visible

## 3. Auth flow

### Create a user

```bash
curl -X POST https://YOUR-API-DOMAIN/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@dfhc.test",
    "password": "StrongPass123",
    "full_name": "DFHC Admin",
    "is_active": true
  }'
```

Expected result:

- `201 Created`, or `400` if the email already exists

### Get token

```bash
curl -X POST https://YOUR-API-DOMAIN/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@dfhc.test&password=StrongPass123"
```

Expected result:

- `200 OK`
- JSON includes `access_token`

## 4. Clients auth gate

### Without token

```bash
curl https://YOUR-API-DOMAIN/clients/
```

Expected result:

- `401 Unauthorized`

### With token

```bash
curl https://YOUR-API-DOMAIN/clients/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Expected result:

- `200 OK`

## 5. Create a client

```bash
curl -X POST https://YOUR-API-DOMAIN/clients/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "full_name": "Mary Johnson",
    "date_of_birth": "1980-05-15",
    "diagnosis": "Cerebral Palsy",
    "address": "123 Main St, Detroit, MI 48201",
    "phone": "313-555-1234",
    "emergency_contact_name": "James Johnson",
    "emergency_contact_phone": "313-555-5678",
    "medicaid_id": "MI12345678",
    "is_active": true,
    "notes": "Requires wheelchair access"
  }'
```

Expected result:

- `201 Created`
- JSON includes a numeric `id`

## 6. Failure conditions to stop launch

Do not proceed with frontend integration if any of these happen:

- `/health` fails
- `/docs` does not load
- `/auth/token` fails for a valid user
- `/clients/` is reachable without a token
- Database migration errors appear in logs

## 7. Launch decision

Frontend integration is allowed only after all checks above pass.
