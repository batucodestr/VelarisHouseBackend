# Velaris House — Backend

Django + Django REST Framework API for the Velaris House hotel reservation system. Handles user accounts, room inventory, and reservations; issues JWT access/refresh tokens for the frontend (`Velaris-House-Frontend/artifacts/hotel-reserve`).

## Stack

- Python 3.12, Django 5.2, Django REST Framework
- Auth: `djangorestframework-simplejwt` (JWT, bearer token)
- CORS: `django-cors-headers`
- DB: SQLite (`db.sqlite3`) — dev only

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin/ and room CRUD
python manage.py runserver
```

Server runs at `http://127.0.0.1:8000`. All API routes are under `/api/`.

`migrate` also seeds 6 demo rooms (see `rooms/migrations/0005_seed_rooms.py`) so the frontend has real data to show out of the box. Delete or edit them via `/admin/` or the room admin endpoints once you have real inventory.

## Configuration notes

- No `.env` layer yet — everything is hardcoded in `app/settings.py` (dev-only `SECRET_KEY`, `DEBUG=True`, SQLite). Don't deploy this settings file as-is.
- `CORS_ALLOW_ALL_ORIGINS = DEBUG` — fine for local dev, tighten before any real deployment.
- JWT lifetimes: 30 min access / 7 day refresh (`SIMPLE_JWT` in `app/settings.py`).
- Reservations whose `check_out` date has passed are lazily flipped from `active` to `completed` on the next list/detail/create request (`reservations/views.py:auto_complete_reservations`) — there's no background scheduler in this project.

## API overview

All error responses share one shape: `{"detail": "...", "errors": {...} }` (see `core/exceptions.py`). List endpoints are paginated (`{"count", "next", "previous", "results"}`, page size 10).

### Accounts (`/api/`) — public

| Method | Path | Body | Notes |
|---|---|---|---|
| POST | `register/` | `username, email, password, phone_number` | Creates `User` + `UserProfile` |
| POST | `login/` | `username, password` | Returns `{access, refresh}` |
| POST | `token/refresh/` | `refresh` | Returns `{access}` |
| POST | `token/verify/` | `token` | 200 if valid |

Authenticated requests send `Authorization: Bearer <access>`.

### Rooms (`/api/rooms/`)

| Method | Path | Auth | Notes |
|---|---|---|---|
| GET | `rooms/` | Public | List (active + inactive) |
| GET | `rooms/<id>/` | Public | Full detail incl. description, amenities, gallery |
| POST | `rooms/create/` | Admin (`is_staff`) | |
| GET/PUT/PATCH | `rooms/<id>/update/` | Admin | |
| DELETE | `rooms/<id>/destroy/` | Admin | |

### Reservations (`/api/reservations/`)

| Method | Path | Auth | Notes |
|---|---|---|---|
| GET | `reservations/` | User | Own reservations (staff see all) |
| POST | `reservations/create/` | User | `{room, check_in, check_out}`; enforces one active reservation per user and no date overlap per room |
| GET | `reservations/<id>/` | User (owner) | |
| DELETE | `reservations/<id>/` | User (owner) | Hard delete — used for both "cancel upcoming" and "remove old record" in the frontend |

## Frontend

The companion frontend lives in a separate repo/folder: `Velaris-House-Frontend/artifacts/hotel-reserve`. Point its `VITE_API_BASE_URL` at this server's `/api` (see that project's README).
