# Flight Assistant

Semester-end project — Desktop Systems Engineering, Mahon Tal.

See `PRD.md` for the full product/architecture spec.

## Project structure

```
flight-assistant/
├── PRD.md
├── docker-compose.yml
├── .env                  # Postgres credentials for docker-compose (not committed)
├── back/
│   ├── app/
│   │   ├── api/
│   │   │   ├── queries/      # GET endpoints (read-only)
│   │   │   └── commands/     # POST endpoints (write)
│   │   ├── services/         # business logic (event sourcing, etc.)
│   │   ├── gateway.py         # calls to AviationStack / Ollama
│   │   ├── models.py          # Pydantic models (API layer)
│   │   ├── db_models.py       # SQLAlchemy models (DB layer)
│   │   ├── database.py
│   │   ├── config.py
│   │   └── main.py
│   ├── requirements.txt
│   └── .env               # AviationStack API key + DB URL (not committed)
└── front/                 # PySide6 app (not started yet)
```

## Backend setup (already done by Sarah, for reference)

1. Python 3.12+ recommended (3.14 works for the back, but PySide6 may not support it yet for the front — check before installing)
2. `cd back && python -m venv venv && venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
3. `pip install -r requirements.txt`
4. Create `back/.env` with:
   ```
   AVIATIONSTACK_API_KEY=your_key_here
   DATABASE_URL=postgresql://flight_admin:change_me_local_only@localhost:5434/flight_assistant
   ```
5. Create a `.env` at the project root (for docker-compose) with:
   ```
   POSTGRES_USER=flight_admin
   POSTGRES_PASSWORD=change_me_local_only
   POSTGRES_DB=flight_assistant
   ```
6. From the project root: `docker compose up -d`
7. From `back/`: `uvicorn app.main:app --reload`
8. Open `http://127.0.0.1:8000/docs` to see and test all endpoints

## Available endpoints (for front development)

### Flights (read-only, calls AviationStack)
- `GET /flights?dep_iata=JFK&limit=5` — search flights departing from an airport

### Bookings (CQRS + Event Sourcing)
- `GET /bookings` — list all bookings (current state)
- `GET /bookings/{booking_id}` — get one booking's current state
- `GET /bookings/{booking_id}/history` — get the raw event log for a booking
- `POST /bookings` — create a booking, body: `{"flight_number": str, "passenger_name": str}`
- `POST /bookings/{booking_id}/confirm` — confirm a booking
- `POST /bookings/{booking_id}/cancel` — cancel a booking

### Not built yet
- Authentication / login (course requirement #2)
- AI advisor / RAG endpoint (course requirement 3.4)
- Flight details as a separate endpoint (currently included in search results)

## Notes for the front (PySide6)

- The front talks to the back exclusively via HTTP/JSON (e.g. with `requests` or `httpx`), never touches the database directly.
- Base URL during development: `http://127.0.0.1:8000`
- Expected patterns: MVP (Model-View-Presenter) per screen, split into microfrontends (SearchModule, DetailsModule, ChartModule, AIAdvisorModule, BookingModule)
