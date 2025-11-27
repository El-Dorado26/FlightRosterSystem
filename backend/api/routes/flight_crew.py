#Async Functions: Allows FastAPI to handle multiple requests at once.
#Extra features: CRUD endpoints, language management, filtering. 
#Checklist: Pilot ID, info, vehicle restriction, allowed range, seniority level. 
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

# Import the core files
from core.database import get_db
from core.models import FlightCrew, PilotLanguage, VehicleType, FlightCrewAssignment
from core.schemas import (
    FlightCrewCreate,
    FlightCrewUpdate,
    FlightCrewResponse,
    PilotLanguageResponse,
    FlightCrewAssignmentCreate,
    FlightCrewAssignmentResponse,
)



router = APIRouter()



# MAIN ENDPOINTS

@router.get("/", response_model=List[FlightCrewResponse])
async def list_flight_crew(
    vehicle_type: Optional[str] = None,
    seniority_level: Optional[str] = None,
    min_allowed_range: Optional[int] = None,
    db: Session = Depends(get_db)
):
    
    '''
    List all flight crew members with optional filters.
    Covers the points (Pilot vehicle type restriction, Pilot seniority level, and Minimum allowed flight range).
    '''
    
    # Start with base query
    query = db.query(FlightCrew)
    
    # Apply filters if provided
    if vehicle_type:
        # Join with VehicleType table to filter by aircraft name
        query = query.join(VehicleType, FlightCrew.vehicle_type_restriction_id == VehicleType.id)
        query = query.filter(VehicleType.aircraft_name == vehicle_type)
    
    if seniority_level:
        query = query.filter(FlightCrew.seniority_level == seniority_level.lower())
    
    if min_allowed_range is not None:
        query = query.filter(FlightCrew.max_allowed_distance_km >= min_allowed_range)
    
    # Execute query and return results
    crew_members = query.all()
    return crew_members


@router.get("/{crew_id}", response_model=FlightCrewResponse)
async def get_flight_crew(crew_id: int, db: Session = Depends(get_db)):
    #Get a unique flight crew member by their ID.
    
    crew = db.query(FlightCrew).filter(FlightCrew.id == crew_id).first()
    
    if not crew:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flight crew member with ID {crew_id} not found"
        )
    
    return crew


@router.post("/", response_model=FlightCrewResponse, status_code=status.HTTP_201_CREATED)
async def create_flight_crew(crew: FlightCrewCreate, db: Session = Depends(get_db)):
    #Create a new flight crew member
    
   #Check seniority level validity
    valid_seniority = ["senior", "junior", "trainee"]
    if crew.seniority_level.lower() not in valid_seniority:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid seniority level. Must be one of: {valid_seniority}"
        )
    
    # Check if employee_id already exists
    existing = db.query(FlightCrew).filter(FlightCrew.employee_id == crew.employee_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Employee ID {crew.employee_id} already exists"
        )
    
    # Check if license_number already exists
    existing_license = db.query(FlightCrew).filter(FlightCrew.license_number == crew.license_number).first()
    if existing_license:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"License number {crew.license_number} already exists"
        )
    
    # Check vehicle type
    if crew.vehicle_type_restriction_id:
        vehicle = db.query(VehicleType).filter(VehicleType.id == crew.vehicle_type_restriction_id).first()
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vehicle type with ID {crew.vehicle_type_restriction_id} not found"
            )
    
    # Create new crew member (without languages first)
    new_crew = FlightCrew(
        name=crew.name,
        age=crew.age,
        gender=crew.gender,
        nationality=crew.nationality,
        employee_id=crew.employee_id,
        role=crew.role,
        license_number=crew.license_number,
        seniority_level=crew.seniority_level.lower(),
        max_allowed_distance_km=crew.max_allowed_distance_km,
        vehicle_type_restriction_id=crew.vehicle_type_restriction_id,
        hours_flown=crew.hours_flown
    )
    
    # Add to database
    db.add(new_crew)
    db.commit()
    db.refresh(new_crew)
    
    # Add languages if provided
    if crew.languages:
        for lang in crew.languages:
            pilot_language = PilotLanguage(
                pilot_id=new_crew.id,
                language=lang.capitalize()
            )
            db.add(pilot_language)
        db.commit()
        db.refresh(new_crew)
    
    return new_crew

#Update a flight crew member
@router.put("/{crew_id}", response_model=FlightCrewResponse)
async def update_flight_crew(
    crew_id: int, 
    crew: FlightCrewUpdate, 
    db: Session = Depends(get_db)
):
    
    
    # Find the crew member
    existing_crew = db.query(FlightCrew).filter(FlightCrew.id == crew_id).first()
    
    if not existing_crew:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flight crew member with ID {crew_id} not found"
        )
    
    
    if crew.seniority_level:
        valid_seniority = ["senior", "junior", "trainee"]
        if crew.seniority_level.lower() not in valid_seniority:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid seniority level. Must be one of: {valid_seniority}"
            )
        existing_crew.seniority_level = crew.seniority_level.lower()
    
    # Update only provided fields
    if crew.hours_flown is not None:
        existing_crew.hours_flown = crew.hours_flown
    
    if crew.role is not None:
        existing_crew.role = crew.role
    
    if crew.max_allowed_distance_km is not None:
        existing_crew.max_allowed_distance_km = crew.max_allowed_distance_km
    
    # Commit changes
    db.commit()
    db.refresh(existing_crew)
    
    return existing_crew

#Delete a Flight Crew Member
@router.delete("/{crew_id}", status_code=status.HTTP_200_OK)
async def delete_flight_crew(crew_id: int, db: Session = Depends(get_db)):
    
    
    crew = db.query(FlightCrew).filter(FlightCrew.id == crew_id).first()
    
    if not crew:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flight crew member with ID {crew_id} not found"
        )
    
    crew_name = crew.name
    
    # Delete associated languages first (due to foreign key constraint)
    db.query(PilotLanguage).filter(PilotLanguage.pilot_id == crew_id).delete()
    
    # Delete the crew member
    db.delete(crew)
    db.commit()
    
    return {
        "message": f"Flight crew member {crew_name} (ID: {crew_id}) deleted successfully",
        "deleted_id": crew_id
    }



# LANGUAGE MANAGEMENT ENDPOINTS

#Add a language to a pilot
@router.post("/{crew_id}/languages", response_model=PilotLanguageResponse, status_code=status.HTTP_201_CREATED)
async def add_language_to_pilot(
    crew_id: int, 
    language: str, 
    db: Session = Depends(get_db)
):
    
    
    # Check if pilot exists
    crew = db.query(FlightCrew).filter(FlightCrew.id == crew_id).first()
    if not crew:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flight crew member with ID {crew_id} not found"
        )
    
    # Check if language already exists
    existing = db.query(PilotLanguage).filter(
        PilotLanguage.pilot_id == crew_id,
        PilotLanguage.language.ilike(language)  # Case-insensitive comparison
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Pilot already knows {language}"
        )
    
    # Add language
    new_language = PilotLanguage(
        pilot_id=crew_id,
        language=language.capitalize()
    )
    
    db.add(new_language)
    db.commit()
    db.refresh(new_language)
    
    return new_language

#Remove a language from a pilot
@router.delete("/{crew_id}/languages/{language}", status_code=status.HTTP_200_OK)
async def remove_language_from_pilot(
    crew_id: int, 
    language: str, 
    db: Session = Depends(get_db)
):
   
    
    # Check if pilot exists
    crew = db.query(FlightCrew).filter(FlightCrew.id == crew_id).first()
    if not crew:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flight crew member with ID {crew_id} not found"
        )
    
    # Find the language
    pilot_language = db.query(PilotLanguage).filter(
        PilotLanguage.pilot_id == crew_id,
        PilotLanguage.language.ilike(language)  # Case-insensitive
    ).first()
    
    if not pilot_language:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Language {language} not found for pilot {crew_id}"
        )
    
    # Delete the language
    db.delete(pilot_language)
    db.commit()
    
    return {
        "message": f"Language {language} removed from pilot {crew_id}",
        "removed_language": language
    }

#Get all languages known by a pilot
@router.get("/{crew_id}/languages", response_model=List[PilotLanguageResponse])
async def get_pilot_languages(crew_id: int, db: Session = Depends(get_db)):
    
    
    # Check if pilot exists
    crew = db.query(FlightCrew).filter(FlightCrew.id == crew_id).first()
    if not crew:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flight crew member with ID {crew_id} not found"
        )
    
    # Get all languages
    languages = db.query(PilotLanguage).filter(PilotLanguage.pilot_id == crew_id).all()
    
    return languages

#Get pilots by seniority level
@router.get("/seniority/{level}", response_model=List[FlightCrewResponse])
async def get_pilots_by_seniority(level: str, db: Session = Depends(get_db)):
    
    # level: Must be one of: senior, junior, trainee
    
    valid_levels = ["senior", "junior", "trainee"]
    level_lower = level.lower()
    
    if level_lower not in valid_levels:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid seniority level '{level}'. Must be one of: {valid_levels}"
        )
    
    crew_members = db.query(FlightCrew).filter(FlightCrew.seniority_level == level_lower).all()
    
    return crew_members

#########################################################################################################################
# Each flight should contain at least one single and one junior pilot where some flights may involve at most two trainees.
#########################################################################################################################
@router.post("/assign", response_model=FlightCrewAssignmentResponse)
async def assign_pilot_to_flight(assignment: FlightCrewAssignmentCreate, db: Session = Depends(get_db)):
    '''
    Assign a pilot to a flight.
    - Each flight must have at least 1 senior pilot
    - Each flight must have at least 1 junior pilot  
    - Each flight can have at most 2 trainees
    '''
    # Get the pilot to assign
    pilot = db.query(FlightCrew).filter(FlightCrew.id == assignment.crew_id).first()
    if not pilot:
        raise HTTPException(status_code=404, detail="Pilot not found")
    
    # Check if pilot is already assigned to this flight
    existing_assignment = db.query(FlightCrewAssignment).filter(
        FlightCrewAssignment.flight_id == assignment.flight_id,
        FlightCrewAssignment.crew_id == assignment.crew_id
    ).first()
    
    if existing_assignment:
        raise HTTPException(status_code=400, detail="Pilot already assigned to this flight")
    
    # Get all pilots already assigned to this flight
    assigned_crew = db.query(FlightCrew).join(FlightCrewAssignment).filter(
        FlightCrewAssignment.flight_id == assignment.flight_id
    ).all()

    # Count current trainees 
    trainee_count = sum(1 for c in assigned_crew if c.seniority_level == "trainee")

    # Check trainee limit (at most 2 as in the rules)
    if pilot.seniority_level == "trainee" and trainee_count >= 2:
        raise HTTPException(
            status_code=400, 
            detail="A flight can have at most 2 trainees. This flight already has 2."
        )

    # Create the assignment
    new_assignment = FlightCrewAssignment(
        flight_id=assignment.flight_id,
        crew_id=assignment.crew_id,
        role=assignment.role
    )
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)

    return new_assignment

@router.get("/flights/{flight_id}/validate")
async def validate_flight_crew_requirements(flight_id: int, db: Session = Depends(get_db)):
    '''
    Validate if a flight meets crew requirements:
    - At least 1 senior pilot
    - At least 1 junior pilot
    - At most 2 trainees
    '''
    # Get all pilots assigned to this flight
    assigned_crew = db.query(FlightCrew).join(FlightCrewAssignment).filter(
        FlightCrewAssignment.flight_id == flight_id
    ).all()
    
    if not assigned_crew:
        return {
            "valid": False,
            "message": "No crew assigned to this flight",
            "requirements": {
                "has_senior": False,
                "has_junior": False,
                "trainee_count_valid": True,
                "senior_count": 0,
                "junior_count": 0,
                "trainee_count": 0
            }
        }
    
    # Count seniority levels
    senior_count = sum(1 for c in assigned_crew if c.seniority_level == "senior")
    junior_count = sum(1 for c in assigned_crew if c.seniority_level == "junior")
    trainee_count = sum(1 for c in assigned_crew if c.seniority_level == "trainee")
    
    # Check requirements
    has_senior = senior_count >= 1
    has_junior = junior_count >= 1
    trainee_count_valid = trainee_count <= 2
    
    is_valid = has_senior and has_junior and trainee_count_valid
    
    messages = []
    if not has_senior:
        messages.append("Missing required senior pilot (need at least 1)")
    if not has_junior:
        messages.append("Missing required junior pilot (need at least 1)")
    if not trainee_count_valid:
        messages.append(f"Too many trainees ({trainee_count}/2 maximum)")
    
    return {
        "valid": is_valid,
        "message": "Flight crew meets all requirements" if is_valid else "; ".join(messages),
        "requirements": {
            "has_senior": has_senior,
            "has_junior": has_junior,
            "trainee_count_valid": trainee_count_valid,
            "senior_count": senior_count,
            "junior_count": junior_count,
            "trainee_count": trainee_count,
            "total_crew": len(assigned_crew)
        }
    }
#Get all crew members assigned to a specific flight
@router.get("/flights/{flight_id}/crew", response_model=List[FlightCrewResponse])
async def get_flight_crew_assignments(flight_id: int, db: Session = Depends(get_db)):
    
    
    crew_members = db.query(FlightCrew).join(FlightCrewAssignment).filter(
        FlightCrewAssignment.flight_id == flight_id
    ).all()
    
    if not crew_members:
        raise HTTPException(
            status_code=404,
            detail=f"No crew assigned to flight {flight_id}"
        )
    
    return crew_members

#Remove a pilot from a flight assignment
@router.delete("/flights/{flight_id}/crew/{crew_id}", status_code=status.HTTP_200_OK)
async def unassign_pilot_from_flight(flight_id: int, crew_id: int, db: Session = Depends(get_db)):
    
    
    assignment = db.query(FlightCrewAssignment).filter(
        FlightCrewAssignment.flight_id == flight_id,
        FlightCrewAssignment.crew_id == crew_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=404,
            detail=f"No assignment found for crew {crew_id} on flight {flight_id}"
        )
    
    db.delete(assignment)
    db.commit()
    
    return {
        "message": f"Pilot {crew_id} unassigned from flight {flight_id}",
        "flight_id": flight_id,
        "crew_id": crew_id
    }
