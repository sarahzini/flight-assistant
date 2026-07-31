# PRD — Flight Assistant

## 1. Context
Semester-end project — Desktop Systems Engineering.
Team: Sarah (back) + Nomi (front)

## 2. Product goal
A desktop application that helps an authenticated user search for flights,
view their details, visualize trends (price/schedule), get advice from an
AI agent specialized in the aviation domain (RAG), and simulate a booking
tied to their account.

## 3. Target users
Traveler looking to compare flights and understand aviation domain vocabulary/procedures
without prior expertise.

## 4. Functional scope (mapped to course requirements)

| # | Course requirement | Product feature |
|---|---|---|
| 3.1 | Data search | Search flights by route (origin/destination) and date, via AviationStack |
| 3.2 | Result details | Flight detail screen: airline, schedule, status, airports |
| 3.3 | Chart / table | Visualization (QTCharts) of found flights — e.g. price or schedule by airline |
| 3.4 | AI agent advice | RAG chat on aviation vocabulary, procedures (baggage, connections, delays) |
| 3.5 | Data entry | Simulated flight booking (writes an event into the system) |

## 5. Out of scope (V1)
- Real payment / integration with an actual airline
- Advanced multi-factor authentication (simple auth is enough)
- Multi-language UI support

## 6. Architecture (summary)
- **Front**: PySide6 desktop app, MVP pattern, split into microfrontends
  (SearchModule, DetailsModule, ChartModule, AIAdvisorModule, BookingModule)
- **Gateway**: single entry point to AviationStack, Ollama, (Cloudinary optional)
- **Back**: FastAPI, CQRS (Command = event writes, Query = reconstructed state reads)
- **Persistence**: PostgreSQL (somee.com target, local Postgres in dev), Event Sourcing
- **AI**: Ollama (Docker) + RAG on an aviation knowledge base (to be built)

## 7. Event model (Event Sourcing) — first draft
- `FlightSearchPerformed`
- `BookingCreated`
- `BookingConfirmed`
- `BookingCancelled`

Booking IDs use 7-character alphanumeric codes (uppercase letters + digits)
instead of UUIDs, for human readability — a deliberate simplification
acceptable for a demo-scale project.

## 8. Tech stack
Python 3.14 (back). Python 3.12 or 3.13 recommended for the front if PySide6 has issues with 3.14.

## 9. Methodology
Development follows the PIV loop (Plan, Implement, Validate) for each
coding task: define the task, acceptance criteria and constraints (Plan),
generate the code with the AI agent (Implement), then verify functional
correctness, integration and code quality before moving to the next task
(Validate). Failed validation loops back to Plan with the new information.

## 10. Proposed milestones
1. Environment setup (Git, Docker, Ollama) + back/front skeleton
2. Gateway + AviationStack integration (search + details)
3. CQRS + Event Sourcing on persistence
4. RAG (knowledge base + Ollama)
5. PySide6 front (MVP + microfrontends) wired to the API
6. UX/UI polish + tests + documentation

