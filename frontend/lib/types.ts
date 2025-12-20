export interface Airport {
  id: number;
  airport_code: string;
  airport_name: string;
  city: string;
  country: string;
}

export interface VehicleType {
  id: number;
  aircraft_name: string;
  aircraft_code: string;
  total_seats: number;
  seating_plan: {
    business: number;
    economy: number;
    rows: number;
    seats_per_row: number;
  };
  max_crew: number;
  max_passengers: number;
}

export interface Airline {
  id: number;
  airline_code: string;
  airline_name: string;
  country: string;
}

export interface FlightCrew {
  id: number;
  name: string;
  age: number;
  gender: string;
  nationality: string;
  employee_id: string;
  role: string;
  license_number: string;
  seniority_level: string;
  max_allowed_distance_km: number;
  hours_flown: number;
  languages: string[];
  seat_number?: string;
}

export interface CabinCrew {
  id: number;
  name: string;
  age: number;
  gender: string;
  nationality: string;
  employee_id: string;
  attendant_type: string;
  languages: string[];
  dish_recipes?: string[];
  seat_number?: string;
}

export interface Passenger {
  id: number;
  name: string;
  age: number;
  gender: string;
  nationality: string;
  passport_number: string;
  seat_type: string;
  seat_number?: string;
  parent_id?: number;
  affiliated_passengers?: number[];
}

export interface ConnectingFlight {
  id: number;
  flight_id: number;
  shared_flight_id: number;
  connecting_flight_number: string;
  connecting_airline_id: number;
  created_at?: string;
}

export interface Flight {
  id: number;
  flight_number: string;
  airline: Airline;
  departure_time: string;
  arrival_time: string;
  flight_duration_minutes: number;
  flight_distance_km: number;
  departure_airport: Airport;
  arrival_airport: Airport;
  vehicle_type: VehicleType;
  status: string;
  shared_flight_info?: {
    id: number;
    primary_flight_id: number;
    primary_airline_id: number;
    secondary_airline_id: number;
    secondary_flight_number: string;
    primary_airline?: Airline;
    secondary_airline?: Airline;
    created_at?: string;
  };
  connecting_flight?: ConnectingFlight;
  flight_crew: FlightCrew[];
  cabin_crew: CabinCrew[];
  passengers: Passenger[];
}
