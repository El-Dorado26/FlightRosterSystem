-- ============================================================
-- TABLE: airport_locations
-- ============================================================
CREATE TABLE airport_locations (
    id SERIAL PRIMARY KEY,
    airport_code VARCHAR(3) UNIQUE NOT NULL,
    airport_name VARCHAR(255) NOT NULL,
    city VARCHAR(255) NOT NULL,
    country VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_airport_code ON airport_locations(airport_code);

-- ============================================================
-- TABLE: vehicle_types
-- Aircraft types with seating configuration
-- ============================================================
CREATE TABLE vehicle_types (
    id SERIAL PRIMARY KEY,
    aircraft_name VARCHAR(255) UNIQUE NOT NULL,
    aircraft_code VARCHAR(10) UNIQUE NOT NULL,
    total_seats INT NOT NULL,
    seating_plan JSONB NOT NULL,
    max_crew INT NOT NULL,
    max_passengers INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE: airlines
-- ============================================================
CREATE TABLE airlines (
    id SERIAL PRIMARY KEY,
    airline_code VARCHAR(2) UNIQUE NOT NULL,
    airline_name VARCHAR(255) UNIQUE NOT NULL,
    country VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE: flights
-- Main flights table
-- ============================================================
CREATE TABLE flights (
    id SERIAL PRIMARY KEY,
    flight_number VARCHAR(6) NOT NULL,
    airline_id INT NOT NULL,
    departure_time TIMESTAMP NOT NULL,
    flight_duration_minutes INT NOT NULL,
    flight_distance_km FLOAT NOT NULL,
    departure_airport_id INT NOT NULL,
    arrival_airport_id INT NOT NULL,
    vehicle_type_id INT NOT NULL,
    status VARCHAR(50) DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (airline_id) REFERENCES airlines(id) ON DELETE CASCADE,
    FOREIGN KEY (departure_airport_id) REFERENCES airport_locations(id) ON DELETE CASCADE,
    FOREIGN KEY (arrival_airport_id) REFERENCES airport_locations(id) ON DELETE CASCADE,
    FOREIGN KEY (vehicle_type_id) REFERENCES vehicle_types(id) ON DELETE CASCADE
);

CREATE INDEX idx_flight_number ON flights(flight_number);
CREATE INDEX idx_departure_time ON flights(departure_time);
CREATE INDEX idx_status ON flights(status);

-- Auto-update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_flights_updated_at BEFORE UPDATE ON flights
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- TABLE: shared_flights
-- Code-share flights between airlines
-- ============================================================
CREATE TABLE shared_flights (
    id SERIAL PRIMARY KEY,
    primary_flight_id INT UNIQUE NOT NULL,
    primary_airline_id INT NOT NULL,
    secondary_airline_id INT NOT NULL,
    secondary_flight_number VARCHAR(6) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (primary_flight_id) REFERENCES flights(id) ON DELETE CASCADE,
    FOREIGN KEY (primary_airline_id) REFERENCES airlines(id) ON DELETE CASCADE,
    FOREIGN KEY (secondary_airline_id) REFERENCES airlines(id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE: connecting_flights
-- Connecting flight information (for shared flights)
-- ============================================================
CREATE TABLE connecting_flights (
    id SERIAL PRIMARY KEY,
    flight_id INT UNIQUE NOT NULL,
    shared_flight_id INT NOT NULL,
    connecting_flight_number VARCHAR(6) NOT NULL,
    connecting_airline_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (flight_id) REFERENCES flights(id) ON DELETE CASCADE,
    FOREIGN KEY (shared_flight_id) REFERENCES shared_flights(id) ON DELETE CASCADE,
    FOREIGN KEY (connecting_airline_id) REFERENCES airlines(id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE: flight_crew
-- Pilots and technical crew
-- ============================================================
CREATE TABLE flight_crew (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INT NOT NULL,
    gender VARCHAR(50) NOT NULL,
    nationality VARCHAR(100) NOT NULL,
    employee_id VARCHAR(100) UNIQUE NOT NULL,
    role VARCHAR(100) NOT NULL,
    license_number VARCHAR(100) UNIQUE NOT NULL,
    seniority_level VARCHAR(50) NOT NULL,
    max_allowed_distance_km FLOAT NOT NULL,
    hours_flown INT DEFAULT 0,
    languages JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    flight_id INT,
    FOREIGN KEY (flight_id) REFERENCES flights(id) ON DELETE SET NULL
);

CREATE INDEX idx_employee_id ON flight_crew(employee_id);
CREATE INDEX idx_seniority ON flight_crew(seniority_level);

-- ============================================================
-- TABLE: pilot_vehicle_restrictions
-- Defines which aircraft types each pilot can operate
-- ============================================================
CREATE TABLE pilot_vehicle_restrictions (
    id SERIAL PRIMARY KEY,
    pilot_id INT NOT NULL,
    vehicle_type_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (pilot_id, vehicle_type_id),
    FOREIGN KEY (pilot_id) REFERENCES flight_crew(id) ON DELETE CASCADE,
    FOREIGN KEY (vehicle_type_id) REFERENCES vehicle_types(id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE: cabin_crew
-- Flight attendants and service staff
-- ============================================================
CREATE TABLE cabin_crew (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INT NOT NULL,
    gender VARCHAR(50) NOT NULL,
    nationality VARCHAR(100) NOT NULL,
    employee_id VARCHAR(100) UNIQUE NOT NULL,
    role VARCHAR(100) NOT NULL,
    languages JSONB,
    certifications TEXT,
    dish_recipes JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    flight_id INT,
    FOREIGN KEY (flight_id) REFERENCES flights(id) ON DELETE SET NULL
);

CREATE INDEX idx_crew_employee_id ON cabin_crew(employee_id);
CREATE INDEX idx_crew_role ON cabin_crew(role);

-- ============================================================
-- TABLE: cabin_crew_vehicle_restrictions
-- Defines which aircraft types each cabin crew member can work on
-- ============================================================
CREATE TABLE cabin_crew_vehicle_restrictions (
    id SERIAL PRIMARY KEY,
    cabin_crew_id INT NOT NULL,
    vehicle_type_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (cabin_crew_id, vehicle_type_id),
    FOREIGN KEY (cabin_crew_id) REFERENCES cabin_crew(id) ON DELETE CASCADE,
    FOREIGN KEY (vehicle_type_id) REFERENCES vehicle_types(id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE: passengers
-- Passenger information and bookings
-- ============================================================
CREATE TABLE passengers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INT NOT NULL,
    gender VARCHAR(50) NOT NULL,
    nationality VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    passport_number VARCHAR(100) UNIQUE NOT NULL,
    seat_type VARCHAR(50) NOT NULL,
    seat_number VARCHAR(10),
    parent_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    flight_id INT,
    FOREIGN KEY (flight_id) REFERENCES flights(id) ON DELETE SET NULL,
    FOREIGN KEY (parent_id) REFERENCES passengers(id) ON DELETE SET NULL
);

CREATE INDEX idx_email ON passengers(email);
CREATE INDEX idx_passport ON passengers(passport_number);
CREATE INDEX idx_flight_seat ON passengers(flight_id, seat_number);

-- ============================================================
-- TABLE: affiliated_passengers
-- Tracks passengers traveling together
-- ============================================================
CREATE TABLE affiliated_passengers (
    id SERIAL PRIMARY KEY,
    passenger_id INT NOT NULL,
    affiliated_passenger_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (passenger_id, affiliated_passenger_id),
    FOREIGN KEY (passenger_id) REFERENCES passengers(id) ON DELETE CASCADE,
    FOREIGN KEY (affiliated_passenger_id) REFERENCES passengers(id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE: menus
-- In-flight menus associated with vehicle types
-- ============================================================
CREATE TABLE menus (
    id SERIAL PRIMARY KEY,
    vehicle_type_id INT UNIQUE NOT NULL,
    menu_items JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_type_id) REFERENCES vehicle_types(id) ON DELETE CASCADE
);

-- ============================================================
-- SAMPLE DATA
-- ============================================================

INSERT INTO airport_locations (airport_code, airport_name, city, country) VALUES
('JFK', 'John F. Kennedy International Airport', 'New York', 'USA'),
('LAX', 'Los Angeles International Airport', 'Los Angeles', 'USA'),
('LHR', 'London Heathrow Airport', 'London', 'United Kingdom'),
('CDG', 'Charles de Gaulle Airport', 'Paris', 'France'),
('IST', 'Istanbul Airport', 'Istanbul', 'Turkey');

INSERT INTO airlines (airline_code, airline_name, country) VALUES
('OA', 'OpenAIrlines', 'International'),
('BA', 'British Airways', 'United Kingdom'),
('TK', 'Turkish Airlines', 'Turkey'),
('AA', 'American Airlines', 'USA'),
('AF', 'Air France', 'France');

INSERT INTO vehicle_types (aircraft_name, aircraft_code, total_seats, seating_plan, max_crew, max_passengers) VALUES
('Boeing 737-800', 'B738', 189, '{"economy": 162, "business": 12, "firstClass": 8, "configuration": "3-3"}'::jsonb, 6, 189),
('Airbus A320', 'A320', 180, '{"economy": 150, "business": 12, "firstClass": 8, "configuration": "3-3"}'::jsonb, 6, 180),
('Boeing 777-300ER', 'B77W', 396, '{"economy": 340, "business": 28, "firstClass": 8, "configuration": "3-4-3"}'::jsonb, 10, 396);