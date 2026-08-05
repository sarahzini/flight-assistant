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
│ │ ├── gateway.py # calls to AviationStack / Ollama, Cloudinary airline icon lookup
│ │ ├── models.py # Pydantic models (API layer)
│ │ ├── db_models.py # SQLAlchemy models (DB layer)
│ │ ├── database.py
│ │ ├── config.py
│ │ └── main.py
│ ├── requirements.txt
│ ├── .env.local # local dev config: AviationStack key, local DB URL, SECRET_KEY (not committed)
│ └── .env.cloud # cloud config: AviationStack key, Aiven DB URL, SECRET_KEY (not committed)
└── front/ # PySide6 desktop app — fully implemented (see Front-end below)
├── app/
│ ├── main.py # QApplication entry, login↔main window transitions, graceful shutdown
│ ├── config.py # BASE_URL = http://127.0.0.1:8000
│ ├── api/ # httpx client + endpoint wrappers
│ ├── domain/models.py # dataclasses mirroring backend models
│ ├── shared/ # Session (JWT), AppState, AsyncTaskRunner, theme, remote image + icon cache
│ ├── shell/ # LoginWindow, MainWindow, Sidebar, Search+Details and Bookings+History composition
│ └── modules/ # MVP modules: login, search, details, chart, booking, booking_history, advisor
└── requirements.txt


## Backend setup (one-time, already done by Sarah, for reference)

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

**Note:** the Aiven free tier automatically powers off after a period of inactivity. Check the service status on the Aiven dashboard (and power it back on if needed) before relying on `APP_ENV=cloud` — e.g. the day before a demo.

To stop: `Ctrl+C` in the uvicorn terminal, then `docker compose down` (or leave Docker running in the background, it doesn't hurt).

## Front-end (PySide6)

**Status: Phases 0–7 complete (MVP), plus booking history and Cloudinary icons.** Login → Search (with inline flight details, including manual lookup by flight number) → Chart → Bookings (with per-row history panel) → AI Advisor. The front talks to the API only via HTTP/JSON.

The front talks to the back **only via HTTP/JSON** (`httpx`) — it never touches the database directly. Base URL: `http://127.0.0.1:8000`.

### Front-end setup (one-time)

1. Use **Python 3.12 or 3.13** (PySide6 may not support 3.14 yet).
2. From the project root:
```cmd
   cd front
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
```
   On Mac/Linux, use `source venv/bin/activate` instead of `venv\Scripts\activate`.

### Run the front-end

Start the backend first (see Quick start above), then in a second terminal:

```cmd
cd front
venv\Scripts\activate
python -m app.main
```

You should see the login window. A green "Connected to backend" status means the API is reachable. After login or register, the main shell opens with sidebar navigation; **Log out** returns to the login screen.

### Shared front-end infrastructure

| Piece | Location | Purpose |
|---|---|---|
| Config | `front/app/config.py` | `BASE_URL` for the FastAPI backend |
| API client | `front/app/api/client.py` | `get` / `post`, Bearer auth, HTTP error mapping |
| Endpoint wrappers | `front/app/api/{auth,flights,bookings,advisor}.py` | Typed calls to backend routes |
| Domain models | `front/app/domain/models.py` | `Flight`, `Airline` (incl. `icon_url`), `Booking`, `BookingEvent`, `Token`, `AdvisorAnswer`, etc. |
| Session | `front/app/shared/session.py` | In-memory JWT + `is_authenticated()` |
| App state | `front/app/shared/app_state.py` | Selected flight and search results across modules |
| Async worker | `front/app/shared/async_worker.py` | Runs API calls off the Qt UI thread so the app never freezes (esp. the slow AI Advisor call) |
| Theme | `front/app/shared/theme.py` | Shared colors, spacing/typography scale, and reusable styled widgets (buttons, labels, inputs) used by every screen |
| Remote image | `front/app/shared/remote_image.py` | Downloads a URL into a `QPixmap`/`QLabel` (Qt has no native support for remote images) |
| Icon cache | `front/app/shared/icon_cache.py` | Caches downloaded icons by URL so repeated airlines in a table don't re-download the same image |
| Shell / modules | `front/app/shell/`, `front/app/modules/` | Login, Search+Details, Chart, Bookings+History, Advisor |
| Shell composition | `front/app/shell/search_with_details.py`, `front/app/shell/bookings_with_history.py` | Each pairs two independent microfrontends side by side — composition lives in the shell, not inside either module, to keep microfrontends decoupled |

**MVP modules:** Login, Search (+ inline Details, with manual flight-number lookup), Chart, Bookings (+ Booking History), AI Advisor.

### Cloudinary images

- **Airline icons**: the backend (`gateway.py`) maps an airline's IATA code to a Cloudinary image URL (El Al's logo for `LY`, a generic airplane icon otherwise) and includes it as `icon_url` on every `Airline` object returned by `/flights`. The Search table displays it in a dedicated icon column.
- **Advisor avatar**: a static Cloudinary image shown next to the "AI Advisor" title (`AdvisorView.ADVISOR_ICON_URL`).
- No Cloudinary API key or `.env` entry is needed for this — images are uploaded once manually via the Cloudinary dashboard, and only their public URLs are used (no upload/delete calls from the app).

## Available endpoints (for front development)

### Auth (public)
- `POST /auth/register` — body: `{"email": EmailStr, "password": str}`
- `POST /auth/login` — body: `{"email": EmailStr, "password": str}` → returns `{"access_token": str}`

### Flights (public, calls AviationStack — be mindful of the 100 req/month free quota)
- `GET /flights?dep_iata=JFK&limit=5` — search flights departing from an airport
- `GET /flights/{flight_iata}` — get details for one specific flight (e.g. `LY4257`)

Each `Flight.airline` includes an `icon_url` (Cloudinary) for display.

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
_(nothing outstanding — all course requirements and the optional Cloudinary integration are implemented)_