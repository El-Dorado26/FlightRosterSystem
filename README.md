# Flight Roster System

A comprehensive flight management system for managing flights, crews, passengers, and dynamic roster generation with both SQL and NoSQL database support.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Getting Started](#getting-started)

---

## Features

- User authentication and role-based access control
- Flight management with multiple airlines and airports
- Flight crew management with certifications and language support
- Cabin crew management with type-specific roles
- Passenger booking and seat assignment
- Dynamic roster generation with automatic crew selection
- Redis caching for performance optimization
- MongoDB and PostgreSQL support for roster storage
- CSV/JSON export functionality for rosters and crew

---

## Technology Stack

### Backend
- **Framework**: FastAPI 0.120.4+
- **Server**: Uvicorn 0.38.0+
- **Database (SQL)**: PostgreSQL with SQLAlchemy ORM
- **Database (NoSQL)**: MongoDB
- **Cache**: Redis (Upstash)
- **Authentication**: JWT with python-jose
- **Password Hashing**: Bcrypt
- **Python Version**: 3.12+

### Frontend
- **Framework**: Next.js 15.5.6
- **UI Library**: React 19.1.0
- **Styling**: Tailwind CSS 4
- **UI Components**: Radix UI
- **Build Tool**: Turbopack
- **Type Safety**: TypeScript

### DevOps & Testing
- **Testing**: pytest with asyncio support
- **Code Coverage**: pytest-cov
- **Browser Automation**: Selenium
- **HTTP Client**: httpx
- **Containerization**: Docker

---

## Project Structure

```
FlightRosterSystem/
├── backend/
│   ├── api/
│   │   └── routes/
│   │       ├── auth.py              # Authentication endpoints
│   │       ├── flights.py           # Flight management
│   │       ├── flight_crew.py       # Flight crew CRUD and assignments
│   │       ├── cabin_crew.py        # Cabin crew CRUD and management
│   │       ├── passengers.py        # Passenger bookings and seats
│   │       └── roster.py            # Roster generation and retrieval
│   ├── core/
│   │   ├── database.py              # Database initialization
│   │   ├── auth.py                  # Auth utilities and JWT
│   │   ├── models.py                # SQLAlchemy models
│   │   ├── schemas.py               # Pydantic schemas
│   │   ├── redis.py                 # Redis cache utilities
│   │   ├── mongodb.py               # MongoDB connection and operations
│   │   └── roster_utils.py          # Roster generation logic
│   ├── main.py                       # FastAPI app entry point
│   └── pyproject.toml                # Dependencies
├── frontend/
│   ├── app/                          # Next.js app directory
│   ├── components/                   # React components
│   ├── contexts/                     # React contexts
│   ├── lib/                          # Utility functions
│   ├── package.json                  # Frontend dependencies
│   └── tailwind.config.ts            # Tailwind configuration
└── README.md
```

---

## API Documentation

### Authentication

#### POST `/auth/register`
Register a new user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe",
  "role": "viewer"
}
```

**Response:** `201 Created`
```json
{
  "access_token": "jwt_token_here",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "viewer",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00"
  }
}
```

**Parameters:**
- `email`: Valid email address (required)
- `password`: Minimum 6 characters, max 72 bytes (required)
- `full_name`: User's full name (required)
- `role`: admin, manager, user, or viewer (defaults to viewer)

---

#### POST `/auth/login`
Login with email and password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "jwt_token_here",
  "user": { /* user object */ }
}
```

---

#### GET `/auth/me`
Get current logged-in user information.

**Headers:** `Authorization: Bearer {token}`

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "viewer",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00"
}
```

---

#### POST `/auth/refresh`
Refresh access token using existing valid token.

**Headers:** `Authorization: Bearer {token}`

**Response:** `200 OK`
```json
{
  "access_token": "new_jwt_token",
  "user": { /* user object */ }
}
```

---

### Flights

#### GET `/flight-info/`
Get all flights (lightweight - basic info only).

**Response:** `200 OK` - List of flights with basic information

---

#### GET `/flight-info/{flight_id}`
Get detailed flight information including crew and passengers.

**Response:** `200 OK`
```json
{
  "id": 1,
  "flight_number": "AA1234",
  "airline": { /* airline object */ },
  "departure_airport": { /* airport object */ },
  "arrival_airport": { /* airport object */ },
  "departure_time": "2024-12-20T10:00:00",
  "arrival_time": "2024-12-20T14:00:00",
  "duration_minutes": 240,
  "distance_km": 1200,
  "vehicle_type": { /* aircraft info */ },
  "flight_crew": [ /* crew array */ ],
  "cabin_crew": [ /* cabin crew array */ ],
  "passengers": [ /* passengers array */ ]
}
```

---

#### POST `/flight-info/`
Create a new flight.

**Request Body:**
```json
{
  "flight_number": "AA1234",
  "airline_id": 1,
  "departure_airport_id": 1,
  "arrival_airport_id": 2,
  "vehicle_type_id": 1,
  "departure_time": "2024-12-20T10:00:00",
  "arrival_time": "2024-12-20T14:00:00",
  "duration_minutes": 240,
  "distance_km": 1200,
  "date": "2024-12-20",
  "status": "scheduled"
}
```

**Validation:**
- Flight number format: AANNNN (2 letters + 4 digits)
- All foreign key references must exist

---

#### PUT `/flight-info/{flight_id}`
Update flight status, duration, or distance.

**Request Body:**
```json
{
  "status": "boarding",
  "duration_minutes": 245,
  "distance_km": 1210
}
```

---

#### DELETE `/flight-info/{flight_id}`
Delete a flight (cascades to shared and connecting flight info).

---

#### GET `/flight-info/airlines`
Get all airlines.

---

#### POST `/flight-info/airlines`
Create a new airline.

**Request Body:**
```json
{
  "airline_code": "AA",
  "airline_name": "American Airlines"
}
```

---

#### GET `/flight-info/airports`
Get all airport locations.

---

#### POST `/flight-info/airports`
Create a new airport location.

**Request Body:**
```json
{
  "airport_code": "JFK",
  "airport_name": "John F. Kennedy International",
  "city": "New York",
  "country": "USA"
}
```

**Validation:** Airport code must be 3 uppercase letters (AAA format)

---

#### GET `/flight-info/vehicles`
Get all vehicle types (aircraft).

---

#### POST `/flight-info/vehicles`
Create a new vehicle type.

**Request Body:**
```json
{
  "aircraft_code": "B738",
  "aircraft_name": "Boeing 737-800",
  "total_seats": 189,
  "seating_plan": { /* JSON seating configuration */ }
}
```

---

#### GET `/flight-info/{flight_id}/shared`
Get shared flight code-share information.

---

#### POST `/flight-info/{flight_id}/shared`
Create shared flight (code-share) information.

**Request Body:**
```json
{
  "primary_airline_id": 1,
  "secondary_airline_id": 2,
  "secondary_flight_number": "UA5678"
}
```

---

#### GET `/flight-info/{flight_id}/connecting`
Get connecting flight information.

---

#### POST `/flight-info/{flight_id}/connecting`
Add connecting flight information.

**Request Body:**
```json
{
  "shared_flight_id": 1,
  "connecting_airline_id": 3,
  "connecting_flight_number": "BA9012"
}
```

---

#### GET `/flight-info/flights/{flight_id}/roster/json`
Export flight roster as JSON.

---

#### GET `/flight-info/flights/{flight_id}/roster/csv`
Export flight roster as CSV file.

---

### Flight Crew

#### GET `/flight-crew/`
List all flight crew members with optional filters.

**Query Parameters:**
- `vehicle_type`: Filter by aircraft name
- `seniority_level`: Filter by level (senior, junior, trainee)
- `min_allowed_range`: Filter by minimum allowed distance (km)

---

#### GET `/flight-crew/{crew_id}`
Get a specific flight crew member by ID.

---

#### POST `/flight-crew/`
Create a new flight crew member.

**Request Body:**
```json
{
  "name": "Captain John Smith",
  "age": 45,
  "gender": "Male",
  "nationality": "USA",
  "employee_id": "EMP001",
  "role": "Pilot",
  "license_number": "LIC123456",
  "seniority_level": "senior",
  "max_allowed_distance_km": 5000,
  "vehicle_type_restriction_id": 1,
  "hours_flown": 10000,
  "languages": ["English", "Spanish"]
}
```

**Validation:**
- Seniority level must be: senior, junior, or trainee
- Employee ID and license number must be unique

---

#### PUT `/flight-crew/{crew_id}`
Update flight crew member details.

**Request Body:** (all fields optional)
```json
{
  "role": "First Officer",
  "seniority_level": "junior",
  "max_allowed_distance_km": 4500,
  "hours_flown": 10100
}
```

---

#### DELETE `/flight-crew/{crew_id}`
Delete a flight crew member and associated languages.

---

#### POST `/flight-crew/{crew_id}/languages`
Add a language to a pilot.

**Query Parameters:**
- `language`: Language name (required)

---

#### DELETE `/flight-crew/{crew_id}/languages/{language}`
Remove a language from a pilot.

---

#### GET `/flight-crew/{crew_id}/languages`
Get all languages known by a pilot.

---

#### GET `/flight-crew/seniority/{level}`
Get all pilots by seniority level.

**Path Parameters:**
- `level`: senior, junior, or trainee

---

#### POST `/flight-crew/assign`
Assign a pilot to a flight.

**Request Body:**
```json
{
  "flight_id": 1,
  "crew_id": 5,
  "role": "Captain"
}
```

**Rules:**
- Each flight must have at least 1 senior pilot
- Each flight must have at least 1 junior pilot
- Each flight can have at most 2 trainees

---

#### GET `/flight-crew/flights/{flight_id}/validate`
Validate if a flight meets crew requirements.

**Response:**
```json
{
  "valid": true,
  "message": "Flight crew meets all requirements",
  "requirements": {
    "has_senior": true,
    "has_junior": true,
    "trainee_count_valid": true,
    "senior_count": 1,
    "junior_count": 1,
    "trainee_count": 0,
    "total_crew": 2
  }
}
```

---

#### GET `/flight-crew/flights/{flight_id}/crew`
Get all crew members assigned to a specific flight.

---

#### DELETE `/flight-crew/flights/{flight_id}/crew/{crew_id}`
Unassign a pilot from a flight.

---

#### GET `/flight-crew/export/json`
Export flight crew as JSON with optional filters.

---

#### GET `/flight-crew/export/csv`
Export flight crew as CSV file with optional filters.

---

### Cabin Crew

#### GET `/cabin-crew/`
Get all cabin crew members with Redis caching.

---

#### GET `/cabin-crew/{crew_id}`
Get a specific cabin crew member with caching.

---

#### POST `/cabin-crew/`
Create a new cabin crew member.

**Request Body:**
```json
{
  "name": "Jane Smith",
  "age": 32,
  "gender": "Female",
  "nationality": "USA",
  "employee_id": "CAB001",
  "attendant_type": "chief",
  "languages": ["English", "French"],
  "recipes": null,
  "vehicle_restrictions": [1, 2]
}
```

**Validation:**
- Attendant type must be: chief, regular, or chef
- Chefs must have 2-4 dish recipes
- Employee ID must be unique

---

#### PUT `/cabin-crew/{crew_id}`
Update cabin crew member details.

---

#### DELETE `/cabin-crew/{crew_id}`
Delete a cabin crew member.

---

#### GET `/cabin-crew/type/{attendant_type}`
Get crew members by type (chief, regular, chef).

---

#### GET `/cabin-crew/flight/{flight_id}`
Get all cabin crew members assigned to a specific flight.

---

### Passengers

#### GET `/passenger/`
Get all passengers, optionally filtered by flight.

**Query Parameters:**
- `flight_id`: Filter by flight ID (optional)

---

#### GET `/passenger/{passenger_id}`
Get a specific passenger by ID.

---

#### POST `/passenger/`
Create a new passenger with optional parent-child relationship.

**Query Parameters:**
- `flight_id`: Flight ID (required)
- `seat_number`: Seat assignment (required)
- `parent_id`: Parent passenger ID for child bookings (optional)

**Request Body:**
```json
{
  "name": "John Passenger",
  "email": "john@example.com",
  "phone": "+1234567890",
  "passport_number": "AB12345678"
}
```

**Validation:**
- Seat must be available on the flight
- Parent and child must be on the same flight

---

#### PUT `/passenger/{passenger_id}`
Update passenger details or seat.

**Query Parameters:**
- `seat_number`: New seat assignment (optional)

---

#### DELETE `/passenger/{passenger_id}`
Delete a passenger.

---

#### GET `/passenger/export/json`
Export passengers as JSON, optionally filtered by flight.

---

#### GET `/passenger/export/csv`
Export passengers as CSV file, optionally filtered by flight.

---

### Roster

#### POST `/roster/generate`
Generate a new flight roster with automatic or manual crew selection.

**Request Body:**
```json
{
  "flight_id": 1,
  "roster_name": "Flight AA1234 - Dec 20",
  "generated_by": "admin@example.com",
  "auto_select_crew": true,
  "flight_crew_ids": [],
  "cabin_crew_ids": [],
  "auto_assign_seats": true,
  "database_type": "sql"
}
```

**Parameters:**
- `flight_id`: Flight to create roster for (required)
- `roster_name`: Name/description of roster (required)
- `generated_by`: User generating roster (required)
- `auto_select_crew`: Automatically select qualified crew (boolean)
- `flight_crew_ids`: Manual crew selection IDs (required if auto_select_crew is false)
- `cabin_crew_ids`: Manual cabin crew IDs (required if auto_select_crew is false)
- `auto_assign_seats`: Automatically assign seats to passengers (boolean)
- `database_type`: Save to "sql" (PostgreSQL) or "nosql" (MongoDB)

---

#### GET `/roster/`
List all rosters with optional filters from both SQL and NoSQL databases.

**Query Parameters:**
- `flight_id`: Filter by flight ID (optional)
- `database_type`: Filter by "sql", "nosql", or show both (optional)

---

#### GET `/roster/{roster_id}`
Retrieve a specific roster by ID from SQL or NoSQL database.

---

#### GET `/roster/{roster_id}/export/json`
Export a roster as JSON format.

---

#### GET `/roster/{roster_id}/download/json`
Download roster as a JSON file.

---

#### DELETE `/roster/{roster_id}`
Delete a roster from SQL or NoSQL database.

---

#### GET `/roster/available-flight-crew/{flight_id}`
Get available flight crew for a specific flight.

Returns crew members qualified for the aircraft type.

---

#### GET `/roster/available-cabin-crew/{flight_id}`
Get available cabin crew for a specific flight.

Returns crew members not restricted from the aircraft type.

---

### Health Checks

#### GET `/`
Welcome endpoint with API version.

---

#### GET `/health`
Basic health check.

---

#### GET `/redis-health`
Check Redis connection status.

**Response:**
```json
{
  "status": "healthy",
  "redis": "connected",
  "test_value": "ok"
}
```

---

## Getting Started

### Backend Setup

1. **Clone the repository:**
```bash
git clone https://github.com/El-Dorado26/FlightRosterSystem.git
cd FlightRosterSystem/backend
```

2. **Create virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies with uv:**
```bash
uv pip install -e ".[dev]"
# or simply: uv sync
```

Note: This project uses `uv` for faster and more reliable dependency management. If you don't have uv installed, get it from https://docs.astral.sh/uv/

4. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your database, Redis, and MongoDB credentials
```

5. **Initialize database:**
```bash
python -m core.database
```

6. **Run the server:**
```bash
python main.py
```

Server starts at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
bun install  # or npm install
```

3. **Run development server:**
```bash
bun run dev  # or npm run dev
```

Frontend starts at `http://localhost:3000`

---

## API Base URL

- **Development**: `http://localhost:8000`
- **Documentation (Swagger UI)**: `http://localhost:8000/docs`
- **Alternative Documentation (ReDoc)**: `http://localhost:8000/redoc`
