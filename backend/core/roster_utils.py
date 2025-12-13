import logging
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from core import models

logger = logging.getLogger(__name__)


def select_flight_crew_automatically(
    db: Session,
    vehicle_type: models.VehicleType,
    exclude_ids: List[int] = None
) -> List[models.FlightCrew]:
    exclude_ids = exclude_ids or []
    selected_crew = []
    
    required_roles = {
        'Captain': 1,
        'First Officer': 1,
        'Flight Engineer': 1 if vehicle_type.max_crew >= 3 else 0
    }
    
    for role, count in required_roles.items():
        if count == 0:
            continue
            
        available_crew = db.query(models.FlightCrew).filter(
            models.FlightCrew.role == role,
            ~models.FlightCrew.id.in_(exclude_ids)
        ).all()
        
        qualified_crew = [
            crew for crew in available_crew
            if crew.vehicle_type_restriction_id is None or crew.vehicle_type_restriction_id == vehicle_type.id
        ]
        
        seniority_order = {'Senior': 3, 'Intermediate': 2, 'Junior': 1}
        qualified_crew.sort(
            key=lambda c: seniority_order.get(c.seniority_level, 0),
            reverse=True
        )
        
        for i in range(min(count, len(qualified_crew))):
            selected_crew.append(qualified_crew[i])
            exclude_ids.append(qualified_crew[i].id)
    
    return selected_crew


def select_cabin_crew_automatically(
    db: Session,
    vehicle_type: models.VehicleType,
    exclude_ids: List[int] = None
) -> List[models.CabinCrew]:
    """
    Automatically select cabin crew using greedy approach.
    
    Constraints:
    - Select 1-4 Chief Attendants
    - Select 4-16 Regular Attendants based on aircraft size
    - Select 0-2 Chefs for long-haul/larger flights
    - Check vehicle restrictions
    
    Args:
        db: Database session
        vehicle_type: Aircraft type for the flight
        exclude_ids: List of crew IDs already assigned
        
    Returns:
        List of selected cabin crew members
    """
    exclude_ids = exclude_ids or []
    selected_crew = []
    
    # Determine crew count based on aircraft size
    # Requirements: 1-4 chief, 4-16 regular, 0-2 chef
    if vehicle_type.total_seats < 100:
        chief_count = 1
        regular_count = 4
        chef_count = 0
    elif vehicle_type.total_seats < 200:
        chief_count = 2
        regular_count = 8
        chef_count = 1
    elif vehicle_type.total_seats < 300:
        chief_count = 3
        regular_count = 12
        chef_count = 1
    else:
        chief_count = 4
        regular_count = 16
        chef_count = 2
    
    # Required cabin crew composition
    required_types = {
        'chief': chief_count,
        'regular': regular_count,
        'chef': chef_count
    }
    
    logger.info(f"Selecting cabin crew for {vehicle_type.aircraft_name} ({vehicle_type.total_seats} seats)")
    logger.info(f"Required: {chief_count} chief, {regular_count} regular, {chef_count} chef")
    
    for attendant_type, count in required_types.items():
        if count == 0:
            continue
            
        # Query available cabin crew
        available_crew = db.query(models.CabinCrew).filter(
            models.CabinCrew.attendant_type == attendant_type,
            ~models.CabinCrew.id.in_(exclude_ids),
            models.CabinCrew.flight_id.is_(None)  # Not assigned to another flight
        ).all()
        
        logger.info(f"Found {len(available_crew)} available {attendant_type} attendants")
        
        # Filter by vehicle restrictions
        qualified_crew = [
            crew for crew in available_crew
            if crew.vehicle_restrictions is None or 
               vehicle_type.id in crew.vehicle_restrictions
        ]
        
        logger.info(f"After vehicle restrictions: {len(qualified_crew)} qualified {attendant_type} attendants")
        
        # Select required count
        selected_count = min(count, len(qualified_crew))
        for i in range(selected_count):
            selected_crew.append(qualified_crew[i])
            exclude_ids.append(qualified_crew[i].id)
        
        logger.info(f"Selected {selected_count}/{count} {attendant_type} attendants")
        
        if selected_count < count:
            logger.warning(f"⚠️  Not enough {attendant_type} attendants! Need {count}, only found {selected_count}")
    
    logger.info(f"Total cabin crew selected: {len(selected_crew)}")
    return selected_crew


def assign_seats_to_passengers(
    passengers: List[models.Passenger],
    seating_plan: Dict[str, Any],
    reserved_seats: List[str] = None
) -> Dict[int, str]:
    """
    Assign seat numbers to passengers who don't have seats.
    
    Constraints:
    - Respect seating plan structure
    - Avoid reserved seats (crew seats, emergency exits if restricted)
    - Use greedy assignment (fill seats sequentially)
    
    Args:
        passengers: List of passengers
        seating_plan: Aircraft seating plan (JSON structure)
        reserved_seats: List of seat numbers that are reserved
        
    Returns:
        Dictionary mapping passenger_id to seat_number
    """
    reserved_seats = set(reserved_seats or [])
    seat_assignments = {}
    
    if seating_plan is None or not isinstance(seating_plan, dict):
        logger.warning(f"Invalid seating plan: {type(seating_plan)} = {seating_plan}, using default simple assignment")
        seat_letters = ['A', 'B', 'C', 'D', 'E', 'F']
        available_seats = []
        for row in range(1, 51):  # Up to 50 rows
            for letter in seat_letters:
                seat_number = f"{row}{letter}"
                if seat_number not in reserved_seats:
                    available_seats.append((1, seat_number))
    else:
        available_seats = []
        
        if 'rows' in seating_plan and isinstance(seating_plan['rows'], list):
            for row in seating_plan['rows']:
                row_number = row.get('row_number')
                for seat in row.get('seats', []):
                    seat_letter = seat.get('seat')
                    seat_type = seat.get('type', 'standard')
                    
                    seat_number = f"{row_number}{seat_letter}"
                    if seat_number in reserved_seats:
                        continue
                    priority = {
                        'standard': 1,
                        'economy': 1,
                        'business': 0,  # Assign business class first
                        'exit': 2,      # Assign exit rows last (may have restrictions)
                        'empty': 3
                    }.get(seat_type, 1)
                    
                    available_seats.append((priority, seat_number))
    
    # Sort seats by priority (business first, then standard, then exit)
    available_seats.sort(key=lambda x: x[0])
    
    # Assign seats to passengers without seat numbers
    seat_index = 0
    for passenger in passengers:
        # Check if passenger already has a seat
        passenger_has_seat = hasattr(passenger, 'seat_number') and passenger.seat_number
        
        if not passenger_has_seat and seat_index < len(available_seats):
            _, seat_number = available_seats[seat_index]
            seat_assignments[passenger.id] = seat_number
            reserved_seats.add(seat_number)
            seat_index += 1
    
    return seat_assignments


def validate_crew_selection(
    flight_crew: List[models.FlightCrew],
    cabin_crew: List[models.CabinCrew],
    vehicle_type: models.VehicleType
) -> Tuple[bool, List[str]]:
    """
    Validate that crew selection meets minimum requirements.
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check flight crew requirements
    roles = [crew.role for crew in flight_crew]
    if 'Captain' not in roles:
        errors.append("Missing Captain in flight crew")
    if 'First Officer' not in roles:
        errors.append("Missing First Officer in flight crew")
    
    # Check flight crew seniority requirements
    seniority_levels = [crew.seniority_level for crew in flight_crew]
    if 'Senior' not in seniority_levels:
        errors.append("Missing Senior pilot in flight crew")
    if 'Junior' not in seniority_levels and 'Intermediate' not in seniority_levels:
        errors.append("Missing Junior/Intermediate pilot in flight crew")
    trainee_count = seniority_levels.count('Trainee')
    if trainee_count > 2:
        errors.append(f"Too many trainee pilots (max 2, have {trainee_count})")
    
    # Check cabin crew requirements (1-4 chief, 4-16 regular, 0-2 chef)
    cabin_types = [crew.attendant_type for crew in cabin_crew]
    
    chief_count = cabin_types.count('chief')
    if chief_count < 1 or chief_count > 4:
        errors.append(f"Invalid chief attendants (need 1-4, have {chief_count})")
    
    regular_count = cabin_types.count('regular')
    if regular_count < 4 or regular_count > 16:
        errors.append(f"Invalid regular attendants (need 4-16, have {regular_count})")
    
    chef_count = cabin_types.count('chef')
    if chef_count > 2:
        errors.append(f"Too many chefs (max 2, have {chef_count})")
    
    for crew in flight_crew:
        if crew.vehicle_type_restriction_id is not None and crew.vehicle_type_restriction_id != vehicle_type.id:
            errors.append(f"Flight crew {crew.name} is restricted from flying {vehicle_type.aircraft_name}")
    
    for crew in cabin_crew:
        if crew.vehicle_restrictions and vehicle_type.id not in crew.vehicle_restrictions:
            errors.append(f"Cabin crew {crew.name} restricted from {vehicle_type.aircraft_name}")
    
    return len(errors) == 0, errors


def get_crew_statistics(
    flight_crew: List[models.FlightCrew],
    cabin_crew: List[models.CabinCrew]
) -> Dict[str, Any]:
    """
    Calculate statistics about selected crew.
    
    Returns:
        Dictionary with crew statistics
    """
    return {
        'total_flight_crew': len(flight_crew),
        'total_cabin_crew': len(cabin_crew),
        'flight_crew_roles': {
            role: sum(1 for c in flight_crew if c.role == role)
            for role in set(c.role for c in flight_crew)
        },
        'cabin_crew_types': {
            type_: sum(1 for c in cabin_crew if c.attendant_type == type_)
            for type_ in set(c.attendant_type for c in cabin_crew)
        },
        'seniority_distribution': {
            level: sum(1 for c in flight_crew if c.seniority_level == level)
            for level in set(c.seniority_level for c in flight_crew)
        }
    }
