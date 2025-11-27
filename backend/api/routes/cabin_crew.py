from fastapi import APIRouter, HTTPException
from typing import List
import sqlite3

from core.schemas import CabinCrewResponse, CabinCrewCreate, CabinCrewUpdate

router = APIRouter()
DB = "airline.db"


def get_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


# --------------------- ENDPOINTS --------------------- #

@router.get("/", response_model=List[CabinCrewResponse])
def list_cabin_crew():
    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT * FROM attendants")
    attendants = []

    for att in c.fetchall():
        att_dict = dict(att)

        # languages
        c.execute(
            "SELECT language FROM attendant_languages WHERE attendant_id = ?",
            (att["attendant_id"],),
        )
        att_dict["languages"] = [row["language"] for row in c.fetchall()]

        # vehicle restrictions
        c.execute(
            "SELECT vehicle_type FROM attendant_vehicle_restrictions WHERE attendant_id = ?",
            (att["attendant_id"],),
        )
        att_dict["vehicle_restrictions"] = [row["vehicle_type"] for row in c.fetchall()]

        # recipes (only for chefs)
        c.execute(
            "SELECT recipe FROM attendant_recipes WHERE attendant_id = ?",
            (att["attendant_id"],),
        )
        att_dict["recipes"] = [row["recipe"] for row in c.fetchall()]

        attendants.append(att_dict)

    conn.close()
    return attendants


@router.get("/{attendant_id}", response_model=CabinCrewResponse)
def get_cabin_crew(attendant_id: int):
   
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
    c.execute(
        "SELECT language FROM attendant_languages WHERE attendant_id = ?",
        (attendant_id,),
    )
    att_dict["languages"] = [row["language"] for row in c.fetchall()]

    # vehicle restrictions
    c.execute(
        "SELECT vehicle_type FROM attendant_vehicle_restrictions WHERE attendant_id = ?",
        (attendant_id,),
    )
    att_dict["vehicle_restrictions"] = [row["vehicle_type"] for row in c.fetchall()]

    # recipes
    c.execute(
        "SELECT recipe FROM attendant_recipes WHERE attendant_id = ?",
        (attendant_id,),
    )
    att_dict["recipes"] = [row["recipe"] for row in c.fetchall()]

    conn.close()
    return att_dict


@router.post("/", response_model=CabinCrewResponse)
def create_cabin_crew(crew: CabinCrewCreate):
    
    conn = get_conn()
    c = conn.cursor()

    c.execute(
        "INSERT INTO attendants (name, role) VALUES (?, ?)",
        (crew.name, crew.role),
    )
    crew_id = c.lastrowid
    conn.commit()
    conn.close()
    # include keys even when values are None
    crew_data = crew.model_dump(exclude_none=False)
    return {**crew_data, "id": crew_id}


@router.put("/{crew_id}", response_model=CabinCrewResponse)
def update_cabin_crew(crew_id: int, crew: CabinCrewUpdate):
    
    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT * FROM attendants WHERE attendant_id = ?", (crew_id,))
    if not c.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Attendant not found")

    c.execute(
        "UPDATE attendants SET name = ?, role = ? WHERE attendant_id = ?",
        (crew.name, crew.role, crew_id),
    )
    conn.commit()
    conn.close()
    crew_data = crew.model_dump(exclude_none=False)
    return {**crew_data, "id": crew_id}


@router.delete("/{crew_id}")
def delete_cabin_crew(crew_id: int):
   
    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT * FROM attendants WHERE attendant_id = ?", (crew_id,))
    if not c.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Attendant not found")

    c.execute("DELETE FROM attendants WHERE attendant_id = ?", (crew_id,))
    conn.commit()
    conn.close()
    return {"detail": "Attendant deleted"}
