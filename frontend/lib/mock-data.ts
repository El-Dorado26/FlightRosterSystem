// Mock data for Flight Roster System

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

export interface Flight {
  id: number;
  flight_number: string;
  airline: Airline;
  departure_time: string;
  flight_duration_minutes: number;
  flight_distance_km: number;
  departure_airport: Airport;
  arrival_airport: Airport;
  vehicle_type: VehicleType;
  status: string;
  shared_flight?: {
    secondary_airline: Airline;
    secondary_flight_number: string;
    connecting_flight?: string;
  };
  flight_crew: FlightCrew[];
  cabin_crew: CabinCrew[];
  passengers: Passenger[];
}

// Mock Airports
export const mockAirports: Airport[] = [
  { id: 1, airport_code: "JFK", airport_name: "John F. Kennedy International", city: "New York", country: "USA" },
  { id: 2, airport_code: "LHR", airport_name: "London Heathrow", city: "London", country: "UK" },
  { id: 3, airport_code: "IST", airport_name: "Istanbul Airport", city: "Istanbul", country: "Turkey" },
  { id: 4, airport_code: "DXB", airport_name: "Dubai International", city: "Dubai", country: "UAE" },
  { id: 5, airport_code: "NRT", airport_name: "Narita International", city: "Tokyo", country: "Japan" },
];

// Mock Airlines
export const mockAirlines: Airline[] = [
  { id: 1, airline_code: "OA", airline_name: "OpenAIrlines", country: "USA" },
  { id: 2, airline_code: "BA", airline_name: "British Airways", country: "UK" },
  { id: 3, airline_code: "TK", airline_name: "Turkish Airlines", country: "Turkey" },
  { id: 4, airline_code: "EK", airline_name: "Emirates", country: "UAE" },
  { id: 5, airline_code: "JL", airline_name: "Japan Airlines", country: "Japan" },
];

// Mock Vehicle Types
export const mockVehicleTypes: VehicleType[] = [
  {
    id: 1,
    aircraft_name: "Boeing 737-800",
    aircraft_code: "B738",
    total_seats: 189,
    seating_plan: { business: 12, economy: 177, rows: 33, seats_per_row: 6 },
    max_crew: 8,
    max_passengers: 189,
  },
  {
    id: 2,
    aircraft_name: "Airbus A350-900",
    aircraft_code: "A359",
    total_seats: 325,
    seating_plan: { business: 36, economy: 289, rows: 52, seats_per_row: 9 },
    max_crew: 15,
    max_passengers: 325,
  },
  {
    id: 3,
    aircraft_name: "Boeing 787-9 Dreamliner",
    aircraft_code: "B789",
    total_seats: 296,
    seating_plan: { business: 30, economy: 266, rows: 48, seats_per_row: 9 },
    max_crew: 12,
    max_passengers: 296,
  },
];

// Mock Flight Crew
export const mockFlightCrew: FlightCrew[] = [
  {
    id: 1,
    name: "Captain John Smith",
    age: 45,
    gender: "Male",
    nationality: "USA",
    employee_id: "FC001",
    role: "Captain",
    license_number: "ATP-12345",
    seniority_level: "Senior",
    max_allowed_distance_km: 15000,
    hours_flown: 12500,
    languages: ["English", "Spanish"],
    seat_number: "Cockpit-Left",
  },
  {
    id: 2,
    name: "First Officer Sarah Johnson",
    age: 32,
    gender: "Female",
    nationality: "UK",
    employee_id: "FC002",
    role: "First Officer",
    license_number: "CPL-67890",
    seniority_level: "Junior",
    max_allowed_distance_km: 10000,
    hours_flown: 3500,
    languages: ["English", "French"],
    seat_number: "Cockpit-Right",
  },
];

// Mock Cabin Crew
export const mockCabinCrew: CabinCrew[] = [
  {
    id: 1,
    name: "Emily Davis",
    age: 35,
    gender: "Female",
    nationality: "USA",
    employee_id: "CC001",
    attendant_type: "Chief",
    languages: ["English", "German"],
    seat_number: "Crew-1A",
  },
  {
    id: 2,
    name: "Michael Brown",
    age: 28,
    gender: "Male",
    nationality: "Canada",
    employee_id: "CC002",
    attendant_type: "Regular",
    languages: ["English", "French"],
    seat_number: "Crew-1B",
  },
  {
    id: 3,
    name: "Lisa Chen",
    age: 30,
    gender: "Female",
    nationality: "China",
    employee_id: "CC003",
    attendant_type: "Regular",
    languages: ["English", "Mandarin"],
    seat_number: "Crew-2A",
  },
  {
    id: 4,
    name: "Chef Marco Rossi",
    age: 38,
    gender: "Male",
    nationality: "Italy",
    employee_id: "CC004",
    attendant_type: "Chef",
    languages: ["English", "Italian"],
    dish_recipes: ["Pasta Carbonara", "Osso Buco", "Tiramisu"],
    seat_number: "Crew-Galley",
  },
];

// Mock Passengers
export const mockPassengers: Passenger[] = [
  {
    id: 1,
    name: "Robert Williams",
    age: 42,
    gender: "Male",
    nationality: "USA",
    passport_number: "P123456789",
    seat_type: "Business",
    seat_number: "1A",
  },
  {
    id: 2,
    name: "Jennifer Martinez",
    age: 35,
    gender: "Female",
    nationality: "Spain",
    passport_number: "P987654321",
    seat_type: "Business",
    seat_number: "1B",
  },
  {
    id: 3,
    name: "David Lee",
    age: 28,
    gender: "Male",
    nationality: "Korea",
    passport_number: "P456789123",
    seat_type: "Economy",
    seat_number: "15C",
  },
  {
    id: 4,
    name: "Maria Garcia",
    age: 31,
    gender: "Female",
    nationality: "Mexico",
    passport_number: "P789123456",
    seat_type: "Economy",
    seat_number: "15D",
  },
  {
    id: 5,
    name: "James Wilson",
    age: 55,
    gender: "Male",
    nationality: "UK",
    passport_number: "P321654987",
    seat_type: "Business",
    seat_number: "2A",
  },
  {
    id: 6,
    name: "Sophie Anderson",
    age: 29,
    gender: "Female",
    nationality: "Sweden",
    passport_number: "P654987321",
    seat_type: "Economy",
    seat_number: "20F",
  },
  {
    id: 7,
    name: "Baby Emma Anderson",
    age: 1,
    gender: "Female",
    nationality: "Sweden",
    passport_number: "P654987322",
    seat_type: "Economy",
    parent_id: 6,
  },
];

// Mock Flights
export const mockFlights: Flight[] = [
  {
    id: 1,
    flight_number: "OA1234",
    airline: mockAirlines[0],
    departure_time: "2025-11-10T14:30:00",
    flight_duration_minutes: 450,
    flight_distance_km: 5500,
    departure_airport: mockAirports[0],
    arrival_airport: mockAirports[1],
    vehicle_type: mockVehicleTypes[2],
    status: "Scheduled",
    flight_crew: mockFlightCrew,
    cabin_crew: mockCabinCrew,
    passengers: mockPassengers,
  },
  {
    id: 2,
    flight_number: "BA5678",
    airline: mockAirlines[1],
    departure_time: "2025-11-12T09:15:00",
    flight_duration_minutes: 240,
    flight_distance_km: 3200,
    departure_airport: mockAirports[1],
    arrival_airport: mockAirports[2],
    vehicle_type: mockVehicleTypes[0],
    status: "Scheduled",
    shared_flight: {
      secondary_airline: mockAirlines[2],
      secondary_flight_number: "TK9012",
    },
    flight_crew: [
      {
        id: 3,
        name: "Captain David Thompson",
        age: 50,
        gender: "Male",
        nationality: "UK",
        employee_id: "FC003",
        role: "Captain",
        license_number: "ATP-54321",
        seniority_level: "Senior",
        max_allowed_distance_km: 12000,
        hours_flown: 15000,
        languages: ["English", "Turkish"],
        seat_number: "Cockpit-Left",
      },
      {
        id: 4,
        name: "First Officer Anna Kowalski",
        age: 29,
        gender: "Female",
        nationality: "Poland",
        employee_id: "FC004",
        role: "First Officer",
        license_number: "CPL-11111",
        seniority_level: "Junior",
        max_allowed_distance_km: 8000,
        hours_flown: 2800,
        languages: ["English", "Polish", "German"],
        seat_number: "Cockpit-Right",
      },
    ],
    cabin_crew: mockCabinCrew.slice(0, 3),
    passengers: mockPassengers.slice(0, 4),
  },
  {
    id: 3,
    flight_number: "TK3456",
    airline: mockAirlines[2],
    departure_time: "2025-11-15T18:45:00",
    flight_duration_minutes: 360,
    flight_distance_km: 4200,
    departure_airport: mockAirports[2],
    arrival_airport: mockAirports[3],
    vehicle_type: mockVehicleTypes[1],
    status: "Boarding",
    flight_crew: [
      {
        id: 5,
        name: "Captain Mehmet Yilmaz",
        age: 48,
        gender: "Male",
        nationality: "Turkey",
        employee_id: "FC005",
        role: "Captain",
        license_number: "ATP-22222",
        seniority_level: "Senior",
        max_allowed_distance_km: 14000,
        hours_flown: 13500,
        languages: ["Turkish", "English", "Arabic"],
        seat_number: "Cockpit-Left",
      },
      {
        id: 6,
        name: "First Officer Ayşe Demir",
        age: 34,
        gender: "Female",
        nationality: "Turkey",
        employee_id: "FC006",
        role: "First Officer",
        license_number: "CPL-33333",
        seniority_level: "Junior",
        max_allowed_distance_km: 9000,
        hours_flown: 4200,
        languages: ["Turkish", "English"],
        seat_number: "Cockpit-Right",
      },
    ],
    cabin_crew: mockCabinCrew,
    passengers: mockPassengers.slice(2, 7),
  },
];
