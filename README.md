# Flight Assistant

Semester-end project — Desktop Systems Engineering, Machon Tal.

See `PRD.md` for the full product/architecture spec.

## Project structure

flight-assistant/
├── PRD.md
├── docker-compose.yml
├── .env # Postgres credentials for docker-compose (not committed)
├── back/
│ ├── app/
│ │ ├── api/
│ │ │ ├── queries/ # GET endpoints (read-only)
│ │ │ └── commands/ # POST endpoints (write)
│ │ ├── services/ # business logic (event sourcing, auth, RAG)
│ │ ├── knowledge_base/ # .txt files used by the RAG advisor
│ │ ├── gateway.py # calls to AviationStack / Ollama
│ │ ├── models.py # Pydantic models (API layer)
│ │ ├── db_models.py # SQLAlchemy models (DB layer)
│ │ ├── database.py
│ │ ├── config.py
│ │ └── main.py
│ ├── requirements.txt
│ ├── .env.local # local dev config: AviationStack key, local DB URL, SECRET_KEY (not committed)
│ └── .env.cloud # cloud config: AviationStack key, Aiven DB URL, SECRET_KEY (not committed)
└── front/ # PySide6 app (not started yet)


## Backend setup (already done)

1. Python 3.12+ recommended (3.14 works for the back, but PySide6 may not support it yet for the front — check before installing)
2. `cd back && python -m venv venv && venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
3. `pip install -r requirements.txt`
4. Create `back/.env.local` (for local development, Docker Postgres) with:

AVIATIONSTACK_API_KEY=your_key_here
DATABASE_URL=postgresql://flight_admin:change_me_local_only@localhost:5434/flight_assistant
SECRET_KEY=your_random_secret_here

5. Create `back/.env.cloud` (for the deployed/cloud database, Aiven) with:

AVIATIONSTACK_API_KEY=your_key_here
DATABASE_URL=postgresql://your_aiven_connection_string?sslmode=require
SECRET_KEY=your_random_secret_here

6. Create a `.env` at the project root (for docker-compose only, local dev) with:

POSTGRES_USER=flight_admin
POSTGRES_PASSWORD=change_me_local_only
POSTGRES_DB=flight_assistant

7. From the project root: `docker compose up -d`
8. Pull the required Ollama models (one-time):

docker exec -it flight_assistant_ollama ollama pull llama3.2
docker exec -it flight_assistant_ollama ollama pull nomic-embed-text


## Quick start (every day, after the one-time setup above)

```cmd
cd flight-assistant
docker compose up -d
cd back
venv\Scripts\activate
uvicorn app.main:app --reload
```

Then open `http://127.0.0.1:8000/docs` to see and test all endpoints.

To use the cloud (Aiven) database instead of local Postgres:
```cmd
set APP_ENV=cloud
uvicorn app.main:app --reload
```
`APP_ENV` defaults to `local` if not set. Local and cloud databases are completely separate — data created in one does not appear in the other.

To stop: `Ctrl+C` in the uvicorn terminal, then `docker compose down` (or leave Docker running in the background, it doesn't hurt).

## Available endpoints (for front development)

### Auth (public)
- `POST /auth/register` — body: `{"email": EmailStr, "password": str}`
- `POST /auth/login` — body: `{"email": EmailStr, "password": str}` → returns `{"access_token": str}`

### Flights (public, calls AviationStack — be mindful of the 100 req/month free quota)
- `GET /flights?dep_iata=JFK&limit=5` — search flights departing from an airport
- `GET /flights/{flight_iata}` — get details for one specific flight (e.g. `LY4257`)

### Bookings (auth required — token via `Authorization: Bearer <token>`)
- `GET /bookings` — list current user's bookings
- `GET /bookings/{booking_id}` — get one booking's current state (owner only, else 403)
- `GET /bookings/{booking_id}/history` — get the raw event log (owner only, else 403)
- `POST /bookings` — create a booking, body: `{"flight_number": str, "passenger_name": str}`
- `POST /bookings/{booking_id}/confirm` — confirm a booking (owner only)
- `POST /bookings/{booking_id}/cancel` — cancel a booking (owner only)

**Note:** `booking_id` is a 7-character alphanumeric code (e.g. `A3K9F2X`), not a UUID — chosen for readability.

### AI Advisor (public, RAG over `knowledge_base/`)
- `POST /advisor` — body: `{"question": str}` → returns `{"answer": str, "sources": [str]}`

### Not built yet
- Cloudinary (optional)

## Notes for the front (PySide6)

- The front talks to the back exclusively via HTTP/JSON (e.g. with `requests` or `httpx`), never touches the database directly.
- Base URL during development: `http://127.0.0.1:8000`
- Store the JWT from `/auth/login` and send it as `Authorization: Bearer <token>` on every booking request.
- Expected patterns: MVP (Model-View-Presenter) per screen, split into microfrontends (SearchModule, DetailsModule, ChartModule, AIAdvisorModule, BookingModule, LoginModule)