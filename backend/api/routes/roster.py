from datetime import datetime
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session, joinedload
import json

from core.database import get_db
from core import models, schemas
from core.mongodb import (
    save_roster_to_mongodb,
    get_roster_from_mongodb,
    list_rosters_from_mongodb,
    delete_roster_from_mongodb
)
from core.roster_utils import (
    select_flight_crew_automatically,
    select_cabin_crew_automatically,
    assign_seats_to_passengers,
    validate_crew_selection,
    get_crew_statistics
)
from core.redis import delete_cache, build_cache_key

router = APIRouter(tags=["roster"])
logger = logging.getLogger(__name__)


@router.post("/generate", response_model=schemas.RosterResponse, status_code=201)
async def generate_roster(
    roster_create: schemas.RosterCreate,
    db: Session = Depends(get_db)
):
    flight = db.query(models.FlightInfo).options(
        joinedload(models.FlightInfo.vehicle_type),
        joinedload(models.FlightInfo.airline),
        joinedload(models.FlightInfo.departure_airport),
        joinedload(models.FlightInfo.arrival_airport)
    ).filter(models.FlightInfo.id == roster_create.flight_id).first()
    
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    
    if not flight.vehicle_type:
        raise HTTPException(status_code=400, detail="Flight must have a vehicle type assigned")
    
    if roster_create.auto_select_crew:
        flight_crew_members = select_flight_crew_automatically(
            db, 
            flight.vehicle_type
        )
        
        for crew in flight_crew_members:
            assignment = models.FlightCrewAssignment(
                flight_id=roster_create.flight_id,
                crew_id=crew.id,
                role=crew.role
            )
            db.add(assignment)
    else:
        # Manual crew selection
        if not roster_create.flight_crew_ids:
            raise HTTPException(status_code=400, detail="flight_crew_ids required for manual selection")
        
        flight_crew_members = db.query(models.FlightCrew).filter(
            models.FlightCrew.id.in_(roster_create.flight_crew_ids)
        ).all()
        
        # Assign manually selected crew to flight
        for crew in flight_crew_members:
            assignment = models.FlightCrewAssignment(
                flight_id=roster_create.flight_id,
                crew_id=crew.id,
                role=crew.role
            )
            db.add(assignment)
    
    if roster_create.auto_select_crew:
        cabin_crew_members = select_cabin_crew_automatically(
            db,
            flight.vehicle_type
        )
    else:
        if not roster_create.cabin_crew_ids:
            raise HTTPException(status_code=400, detail="cabin_crew_ids required for manual selection")
        
        cabin_crew_members = db.query(models.CabinCrew).filter(
            models.CabinCrew.id.in_(roster_create.cabin_crew_ids)
        ).all()
    
    is_valid, errors = validate_crew_selection(
        flight_crew_members,
        cabin_crew_members,
        flight.vehicle_type
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=f"Crew selection validation failed: {'; '.join(errors)}"
        )

    # NOTE: We do NOT set flight_id on crew members
    # Rosters are snapshots/planning documents, not permanent assignments
    # This allows crew to be reused for multiple roster generations

    # Assign cabin crew to flight
    for crew in cabin_crew_members:
        crew.flight_id = roster_create.flight_id

    passengers = db.query(models.Passenger).filter(
        models.Passenger.flight_id == roster_create.flight_id
    ).all()
    
    if roster_create.auto_assign_seats:
        # Get existing seat assignments
        reserved_seats = [p.seat_number for p in passengers if p.seat_number]
        
        # Log seating plan info for debugging
        logger.info(f"Seating plan type: {type(flight.vehicle_type.seating_plan)}")
        logger.info(f"Seating plan value: {flight.vehicle_type.seating_plan}")
        
        # Assign seats to passengers without seat numbers
        seat_assignments = assign_seats_to_passengers(
            passengers,
            flight.vehicle_type.seating_plan,
            reserved_seats
        )
        
        # Update passenger seat numbers in database
        for passenger in passengers:
            if passenger.id in seat_assignments:
                passenger.seat_number = seat_assignments[passenger.id]
    
    db.commit()

    # Invalidate flight cache so updated crew/passenger data is fetched
    try:
        delete_cache("flights:all")
        delete_cache(build_cache_key("flight:{flight_id}", flight_id=roster_create.flight_id))
    except Exception as e:
        logger.warning(f"Failed to invalidate cache: {e}")

    for crew in flight_crew_members:
        db.refresh(crew)
    for crew in cabin_crew_members:
        db.refresh(crew)
    for passenger in passengers:
        db.refresh(passenger)
    
    # Build complete roster data
    roster_data = {
        "flight_info": {
            "id": flight.id,
            "flight_number": flight.flight_number,
            "airline": {
                "id": flight.airline.id,
                "name": flight.airline.airline_name,
                "code": flight.airline.airline_code
            } if flight.airline else None,
            "route": {
                "departure": {
                    "id": flight.departure_airport.id,
                    "code": flight.departure_airport.airport_code,
                    "name": flight.departure_airport.airport_name,
                    "city": flight.departure_airport.city,
                    "country": flight.departure_airport.country
                } if flight.departure_airport else None,
                "arrival": {
                    "id": flight.arrival_airport.id,
                    "code": flight.arrival_airport.airport_code,
                    "name": flight.arrival_airport.airport_name,
                    "city": flight.arrival_airport.city,
                    "country": flight.arrival_airport.country
                } if flight.arrival_airport else None
            },
            "schedule": {
                "departure_time": str(flight.departure_time),
                "arrival_time": str(flight.arrival_time),
                "date": str(flight.date)
            },
            "aircraft": {
                "id": flight.vehicle_type.id,
                "name": flight.vehicle_type.aircraft_name,
                "code": flight.vehicle_type.aircraft_code,
                "total_seats": flight.vehicle_type.total_seats,
                "seating_plan": flight.vehicle_type.seating_plan
            } if flight.vehicle_type else None
        },
        "flight_crew": [
            {
                "id": crew.id,
                "name": crew.name,
                "age": crew.age,
                "gender": crew.gender,
                "nationality": crew.nationality,
                "employee_id": crew.employee_id,
                "role": crew.role,
                "seniority_level": crew.seniority_level,
                "license_number": crew.license_number,
                "languages": [lang.language for lang in crew.languages]
            }
            for crew in flight_crew_members
        ],
        "cabin_crew": [
            {
                "id": crew.id,
                "name": crew.name,
                "age": crew.age,
                "gender": crew.gender,
                "nationality": crew.nationality,
                "employee_id": crew.employee_id,
                "attendant_type": crew.attendant_type,
                "languages": crew.languages,
                "recipes": crew.recipes,
                "vehicle_restrictions": crew.vehicle_restrictions
            }
            for crew in cabin_crew_members
        ],
        "passengers": [
            {
                "id": passenger.id,
                "name": passenger.name,
                "email": passenger.email,
                "phone": passenger.phone,
                "passport_number": passenger.passport_number,
                "seat_number": passenger.seat_number  # Include seat assignment
            }
            for passenger in passengers
        ]
    }
    
    crew_stats = get_crew_statistics(flight_crew_members, cabin_crew_members)
    
    metadata = {
        "total_flight_crew": len(flight_crew_members),
        "total_cabin_crew": len(cabin_crew_members),
        "total_passengers": len(passengers),
        "capacity": flight.vehicle_type.total_seats if flight.vehicle_type else 0,
        "occupancy_rate": (len(passengers) / flight.vehicle_type.total_seats * 100) if flight.vehicle_type and flight.vehicle_type.total_seats > 0 else 0,
        "crew_statistics": crew_stats,
        "seats_assigned": sum(1 for p in passengers if p.seat_number),
        "seats_unassigned": sum(1 for p in passengers if not p.seat_number),
        "auto_crew_selection": roster_create.auto_select_crew,
        "auto_seat_assignment": roster_create.auto_assign_seats
    }
    
    # Save to appropriate database based on user selection
    if roster_create.database_type == "nosql":
        # Save to MongoDB
        mongo_roster_data = {
            "flight_id": roster_create.flight_id,
            "roster_name": roster_create.roster_name,
            "generated_by": roster_create.generated_by,
            "generated_at": datetime.now(),
            "database_type": "nosql",
            "roster_data": roster_data,
            "metadata": metadata
        }
        roster_id = save_roster_to_mongodb(mongo_roster_data)
        
        # Return MongoDB roster with string ID
        return {
            "id": roster_id,
            "flight_id": roster_create.flight_id,
            "roster_name": roster_create.roster_name,
            "generated_by": roster_create.generated_by,
            "generated_at": mongo_roster_data["generated_at"],
            "database_type": "nosql",
            "roster_data": roster_data,
            "metadata": metadata
        }
    else:
        # Save to SQL (PostgreSQL)
        new_roster = models.Roster(
            flight_id=roster_create.flight_id,
            roster_name=roster_create.roster_name,
            generated_by=roster_create.generated_by,
            database_type=roster_create.database_type,
            roster_data=roster_data,
            metadata=metadata
        )
        
        db.add(new_roster)
        db.commit()
        db.refresh(new_roster)
        
        return new_roster


@router.get("/available-flight-crew/{flight_id}")
async def get_available_flight_crew(flight_id: int, db: Session = Depends(get_db)):
    """
    Get available flight crew for a specific flight.
    Returns crew members that are qualified for the aircraft type.
    """
    flight = db.query(models.FlightInfo).filter(models.FlightInfo.id == flight_id).first()
    if not flight or not flight.vehicle_type:
        raise HTTPException(status_code=404, detail="Flight or vehicle type not found")
    
    # Get all flight crew
    all_crew = db.query(models.FlightCrew).all()

    # Filter by vehicle type restrictions
    qualified_crew = [
        {
            "id": crew.id,
            "name": crew.name,
            "role": crew.role,
            "seniority_level": crew.seniority_level,
            "age": crew.age,
            "nationality": crew.nationality,
            "license_number": crew.license_number,
            "languages": [lang.language for lang in crew.languages] if crew.languages else [],
            "qualified": crew.vehicle_type_restriction_id is None or crew.vehicle_type_restriction_id == flight.vehicle_type.id
        }
        for crew in all_crew
    ]

    return qualified_crew


@router.get("/available-cabin-crew/{flight_id}")
async def get_available_cabin_crew(flight_id: int, db: Session = Depends(get_db)):
    """
    Get available cabin crew for a specific flight.
    Returns crew members that are not restricted from the aircraft type.
    """
    flight = db.query(models.FlightInfo).filter(models.FlightInfo.id == flight_id).first()
    if not flight or not flight.vehicle_type:
        raise HTTPException(status_code=404, detail="Flight or vehicle type not found")
    
    # Get all cabin crew not assigned to another flight
    all_crew = db.query(models.CabinCrew).filter(
        models.CabinCrew.flight_id.is_(None)
    ).all()
    
    # Filter by vehicle restrictions
    available_crew = [
        {
            "id": crew.id,
            "name": crew.name,
            "attendant_type": crew.attendant_type,
            "languages": crew.languages,
            "recipes": crew.recipes,
            "vehicle_restrictions": crew.vehicle_restrictions,
            "qualified": crew.vehicle_restrictions is None or flight.vehicle_type.id in crew.vehicle_restrictions
        }
        for crew in all_crew
    ]
    
    return available_crew


@router.get("/")
async def list_rosters(
    flight_id: Optional[int] = None,
    database_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all rosters with optional filters from both SQL and NoSQL databases.
    """
    all_rosters = []
    
    # Get SQL rosters if not filtering for nosql only
    if database_type != "nosql":
        query = db.query(models.Roster)
        
        if flight_id:
            query = query.filter(models.Roster.flight_id == flight_id)
        
        if database_type:
            query = query.filter(models.Roster.database_type == database_type)
        
        sql_rosters = query.order_by(models.Roster.generated_at.desc()).all()
        all_rosters.extend([{
            "id": r.id,
            "flight_id": r.flight_id,
            "roster_name": r.roster_name,
            "generated_by": r.generated_by,
            "generated_at": r.generated_at,
            "database_type": r.database_type
        } for r in sql_rosters])
    
    # Get MongoDB rosters if not filtering for sql only
    if database_type != "sql":
        try:
            mongo_rosters = list_rosters_from_mongodb(flight_id=flight_id)
            all_rosters.extend([{
                "id": r["id"],
                "flight_id": r["flight_id"],
                "roster_name": r["roster_name"],
                "generated_by": r["generated_by"],
                "generated_at": r["generated_at"],
                "database_type": "nosql"
            } for r in mongo_rosters])
        except Exception as e:
            # MongoDB might not be available, skip silently
            print(f"MongoDB not available: {e}")
    
    # Sort by generated_at descending
    all_rosters.sort(key=lambda x: x["generated_at"], reverse=True)
    
    return all_rosters


@router.get("/{roster_id}")
async def get_roster(roster_id: str, db: Session = Depends(get_db)):
    """
    Retrieve a specific roster by ID from either SQL or NoSQL database.
    Tries MongoDB first (if roster_id is not numeric), then SQL.
    """
    # Try MongoDB first if ID looks like MongoDB ObjectId (24 hex characters)
    if len(roster_id) == 24 and all(c in '0123456789abcdef' for c in roster_id.lower()):
        mongo_roster = get_roster_from_mongodb(roster_id)
        if mongo_roster:
            return mongo_roster
    
    # Try SQL database
    try:
        roster_id_int = int(roster_id)
        roster = db.query(models.Roster).filter(models.Roster.id == roster_id_int).first()
        if roster:
            return {
                "id": roster.id,
                "flight_id": roster.flight_id,
                "roster_name": roster.roster_name,
                "generated_by": roster.generated_by,
                "generated_at": roster.generated_at,
                "database_type": roster.database_type,
                "roster_data": roster.roster_data,
                "metadata": roster.metadata
            }
    except ValueError:
        pass
    
    raise HTTPException(status_code=404, detail="Roster not found")


@router.get("/{roster_id}/export/json", response_class=JSONResponse)
async def export_roster_json(roster_id: int, db: Session = Depends(get_db)):
    """
    Export a roster as JSON format.
    """
    roster = db.query(models.Roster).filter(models.Roster.id == roster_id).first()
    
    if not roster:
        raise HTTPException(status_code=404, detail="Roster not found")
    
    export_data = {
        "roster_id": roster.id,
        "roster_name": roster.roster_name,
        "generated_at": roster.generated_at.isoformat(),
        "generated_by": roster.generated_by,
        "database_type": roster.database_type,
        "flight_data": roster.roster_data,
        "metadata": roster.metadata
    }
    
    return JSONResponse(content=export_data)


@router.get("/{roster_id}/download/json")
async def download_roster_json(roster_id: int, db: Session = Depends(get_db)):
    """
    Download roster as a JSON file.
    """
    roster = db.query(models.Roster).filter(models.Roster.id == roster_id).first()
    
    if not roster:
        raise HTTPException(status_code=404, detail="Roster not found")
    
    export_data = {
        "roster_id": roster.id,
        "roster_name": roster.roster_name,
        "generated_at": roster.generated_at.isoformat(),
        "generated_by": roster.generated_by,
        "database_type": roster.database_type,
        "flight_data": roster.roster_data,
        "metadata": roster.metadata
    }
    
    json_content = json.dumps(export_data, indent=2, default=str)
    
    filename = f"roster_{roster.roster_name.replace(' ', '_')}_{roster.id}.json"
    
    return StreamingResponse(
        iter([json_content]),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.delete("/{roster_id}", status_code=204)
async def delete_roster(roster_id: str, db: Session = Depends(get_db)):
    """
    Delete a roster from either SQL or NoSQL database.
    """
    if len(roster_id) == 24 and all(c in '0123456789abcdef' for c in roster_id.lower()):
        if delete_roster_from_mongodb(roster_id):
            return None
    
    try:
        roster_id_int = int(roster_id)
        roster = db.query(models.Roster).filter(models.Roster.id == roster_id_int).first()
        
        if roster:
            db.delete(roster)
            db.commit()
            return None
    except ValueError:
        pass
    
    raise HTTPException(status_code=404, detail="Roster not found")