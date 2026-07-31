from fastapi import FastAPI

from app.api.commands import bookings as booking_commands
from app.api.queries import bookings as booking_queries
from app.api.queries import flights as flight_queries
from app.api.queries import advisor as advisor_queries
from app.api.commands import auth as auth_commands
from app.database import Base, engine
from app.db_models import BookingEventRow, UserRow # noqa: F401 — needed so Base knows about this table

app = FastAPI(title="Flight Assistant API")
Base.metadata.create_all(bind=engine)

@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(flight_queries.router)
app.include_router(booking_queries.router)
app.include_router(booking_commands.router)
app.include_router(auth_commands.router)
app.include_router(advisor_queries.router)
