import sqlite3
from fastapi import FastAPI, HTTPException

app = FastAPI(
    title="Cabin Crew Information API",
    description="Provides cabin crew data (attendants, languages, vehicle restrictions, recipes)",
    version="1.0.0"
)

DB = "airline.db"


def get_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


# --------------------- ENDPOINTS --------------------- #

@app.get("/attendants")
def get_all_attendants():
    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT * FROM attendants")
    attendants = []

    for att in c.fetchall():
        att_dict = dict(att)

        # languages
        c.execute("SELECT language FROM attendant_languages WHERE attendant_id = ?", (att["attendant_id"],))
        att_dict["languages"] = [row["language"] for row in c.fetchall()]

        # vehicle restrictions
        c.execute("SELECT vehicle_type FROM attendant_vehicle_restrictions WHERE attendant_id = ?", (att["attendant_id"],))
        att_dict["vehicle_restrictions"] = [row["vehicle_type"] for row in c.fetchall()]

        # recipes (only chefs)
        c.execute("SELECT recipe FROM attendant_recipes WHERE attendant_id = ?", (att["attendant_id"],))
        att_dict["recipes"] = [row["recipe"] for row in c.fetchall()]

        attendants.append(att_dict)

    conn.close()
    return attendants


@app.get("/attendants/{attendant_id}")
def get_attendant(attendant_id: int):
    conn = get_conn()
    c = conn.cursor()

    # base attendant info
    c.execute("SELECT * FROM attendants WHERE attendant_id = ?", (attendant_id,))
    att = c.fetchone()

    if att is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Attendant not found")

    att_dict = dict(att)

    # languages
    c.execute("SELECT language FROM attendant_languages WHERE attendant_id = ?", (attendant_id,))
    att_dict["languages"] = [row["language"] for row in c.fetchall()]

    # vehicle restrictions
    c.execute("SELECT vehicle_type FROM attendant_vehicle_restrictions WHERE attendant_id = ?", (attendant_id,))
    att_dict["vehicle_restrictions"] = [row["vehicle_type"] for row in c.fetchall()]

    # recipes
    c.execute("SELECT recipe FROM attendant_recipes WHERE attendant_id = ?", (attendant_id,))
    att_dict["recipes"] = [row["recipe"] for row in c.fetchall()]

    conn.close()
    return att_dict
"""Cabin Crew routes."""
from fastapi import APIRouter
from typing import List

from core.schemas import CabinCrewResponse, CabinCrewCreate, CabinCrewUpdate

router = APIRouter()

# Placeholder for mock data (will be replaced with DB queries)
cabin_crew_db: List[dict] = []

@router.get("/", response_model=List[CabinCrewResponse])
async def list_cabin_crew():
    """Get all cabin crew members."""
    pass

@router.get("/{crew_id}", response_model=CabinCrewResponse)
async def get_cabin_crew(crew_id: int):
    """Get a specific cabin crew member by ID."""
    pass

@router.post("/", response_model=CabinCrewResponse)
async def create_cabin_crew(crew: CabinCrewCreate):
    """Create a new cabin crew member."""
    pass

@router.put("/{crew_id}", response_model=CabinCrewUpdate)
async def update_cabin_crew(crew_id: int, crew: CabinCrewUpdate):
    """Update a cabin crew member."""
    pass

@router.delete("/{crew_id}")
async def delete_cabin_crew(crew_id: int):
    """Delete a cabin crew member."""
    pass
