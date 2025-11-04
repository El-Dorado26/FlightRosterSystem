-- ============================================================
-- TABLE: airport_locations
-- Stores airport information with codes and locations
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
-- Stores aircraft types with seating configurations
-- ============================================================
CREATE TABLE vehicle_types (
    id SERIAL PRIMARY KEY,
    aircraft_name VARCHAR(255) UNIQUE NOT NULL,
    aircraft_code VARCHAR(10) UNIQUE NOT NULL,
    total_seats INTEGER NOT NULL CHECK (total_seats > 0),
    seating_plan JSONB NOT NULL,
    max_crew INTEGER NOT NULL CHECK (max_crew > 0),
    max_passengers INTEGER NOT NULL CHECK (max_passengers > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE: menus
-- Stores menu items for each vehicle type
-- ============================================================
CREATE TABLE menus (
    id SERIAL PRIMARY KEY,
    vehicle_type_id INTEGER UNIQUE NOT NULL,
    menu_items JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_vehicle_type 
        FOREIGN KEY (vehicle_type_id) 
        REFERENCES vehicle_types(id) 
        ON DELETE CASCADE
);

-- ============================================================
-- TABLE: airlines
-- Stores airline company information
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
-- Main flights table with schedule and route information
-- ============================================================
CREATE TABLE flights (
    id SERIAL PRIMARY KEY,
    flight_number VARCHAR(6) NOT NULL,
    airline_id INTEGER NOT NULL,
    departure_time TIMESTAMP NOT NULL,
    flight_duration_minutes INTEGER NOT NULL CHECK (flight_duration_minutes > 0),
    flight_distance_km FLOAT NOT NULL CHECK (flight_distance_km > 0),
    departure_airport_id INTEGER NOT NULL,
    arrival_airport_id INTEGER NOT NULL,
    vehicle_type_id INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_airline 
        FOREIGN KEY (airline_id) 
        REFERENCES airlines(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_departure_airport 
        FOREIGN KEY (departure_airport_id) 
        REFERENCES airport_locations(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_arrival_airport 
        FOREIGN KEY (arrival_airport_id) 
        REFERENCES airport_locations(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_vehicle_type 
        FOREIGN KEY (vehicle_type_id) 
        REFERENCES vehicle_types(id) 
        ON DELETE CASCADE,
    CONSTRAINT chk_different_airports 
        CHECK (departure_airport_id != arrival_airport_id)
);

CREATE INDEX idx_flight_number ON flights(flight_number);
CREATE INDEX idx_flights_departure_time ON flights(departure_time);
CREATE INDEX idx_flights_status ON flights(status);

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for flights table
CREATE TRIGGER update_flights_updated_at 
    BEFORE UPDATE ON flights
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- TABLE: shared_flights
-- Tracks code-share flights between airlines
-- ============================================================
CREATE TABLE shared_flights (
    id SERIAL PRIMARY KEY,
    primary_flight_id INTEGER UNIQUE NOT NULL,
    primary_airline_id INTEGER NOT NULL,
    secondary_airline_id INTEGER NOT NULL,
    secondary_flight_number VARCHAR(6) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_primary_flight 
        FOREIGN KEY (primary_flight_id) 
        REFERENCES flights(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_primary_airline 
        FOREIGN KEY (primary_airline_id) 
        REFERENCES airlines(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_secondary_airline 
        FOREIGN KEY (secondary_airline_id) 
        REFERENCES airlines(id) 
        ON DELETE CASCADE,
    CONSTRAINT chk_different_airlines 
        CHECK (primary_airline_id != secondary_airline_id)
);

-- ============================================================
-- TABLE: connecting_flights
-- Tracks connecting flight information
-- ============================================================
CREATE TABLE connecting_flights (
    id SERIAL PRIMARY KEY,
    flight_id INTEGER UNIQUE NOT NULL,
    shared_flight_id INTEGER NOT NULL,
    connecting_flight_number VARCHAR(6) NOT NULL,
    connecting_airline_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_flight 
        FOREIGN KEY (flight_id) 
        REFERENCES flights(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_shared_flight 
        FOREIGN KEY (shared_flight_id) 
        REFERENCES shared_flights(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_connecting_airline 
        FOREIGN KEY (connecting_airline_id) 
        REFERENCES airlines(id) 
        ON DELETE CASCADE
);

-- ============================================================
-- TABLE: flight_crew
-- Stores pilot and technical crew information
-- ============================================================
CREATE TABLE flight_crew (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INTEGER NOT NULL CHECK (age >= 18 AND age <= 70),
    gender VARCHAR(50) NOT NULL,
    nationality VARCHAR(100) NOT NULL,
    employee_id VARCHAR(100) UNIQUE NOT NULL,
    role VARCHAR(100) NOT NULL,
    license_number VARCHAR(100) UNIQUE NOT NULL,
    seniority_level VARCHAR(50) NOT NULL,
    max_allowed_distance_km FLOAT NOT NULL CHECK (max_allowed_distance_km > 0),
    vehicle_type_restriction_id INTEGER,
    hours_flown INTEGER DEFAULT 0 CHECK (hours_flown >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    flight_id INTEGER,
    CONSTRAINT fk_flight 
        FOREIGN KEY (flight_id) 
        REFERENCES flights(id) 
        ON DELETE SET NULL,
    CONSTRAINT fk_vehicle_type_restriction 
        FOREIGN KEY (vehicle_type_restriction_id) 
        REFERENCES vehicle_types(id) 
        ON DELETE SET NULL
);

CREATE INDEX idx_employee_id ON flight_crew(employee_id);
CREATE INDEX idx_flight_crew_license ON flight_crew(license_number);

-- ============================================================
-- TABLE: pilot_languages
-- Stores languages spoken by pilots (many-to-many relationship)
-- ============================================================
CREATE TABLE pilot_languages (
    id SERIAL PRIMARY KEY,
    pilot_id INTEGER NOT NULL,
    language VARCHAR(100) NOT NULL,
    CONSTRAINT fk_pilot 
        FOREIGN KEY (pilot_id) 
        REFERENCES flight_crew(id) 
        ON DELETE CASCADE,
    CONSTRAINT unique_pilot_language 
        UNIQUE (pilot_id, language)
);

CREATE INDEX idx_pilot_languages_pilot ON pilot_languages(pilot_id);

-- ============================================================
-- TABLE: cabin_crew
-- Stores cabin crew and flight attendant information
-- ============================================================
CREATE TABLE cabin_crew (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    employee_id VARCHAR(100) UNIQUE NOT NULL,
    role VARCHAR(100) NOT NULL,
    certifications TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    flight_id INTEGER,
    CONSTRAINT fk_flight 
        FOREIGN KEY (flight_id) 
        REFERENCES flights(id) 
        ON DELETE SET NULL
);

CREATE INDEX idx_cabin_crew_employee_id ON cabin_crew(employee_id);

-- ============================================================
-- TABLE: passengers
-- Stores passenger information and flight bookings
-- ============================================================
CREATE TABLE passengers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    passport_number VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    flight_id INTEGER,
    CONSTRAINT fk_flight 
        FOREIGN KEY (flight_id) 
        REFERENCES flights(id) 
        ON DELETE SET NULL,
    CONSTRAINT chk_valid_email 
        CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE INDEX idx_passengers_email ON passengers(email);
CREATE INDEX idx_passengers_passport ON passengers(passport_number);

-- ============================================================
-- USEFUL VIEWS
-- ============================================================

-- View: Complete flight information with related details
CREATE VIEW flight_details AS
SELECT 
    f.id,
    f.flight_number,
    a.airline_name,
    a.airline_code,
    dep.airport_name AS departure_airport,
    dep.city AS departure_city,
    arr.airport_name AS arrival_airport,
    arr.city AS arrival_city,
    f.departure_time,
    f.flight_duration_minutes,
    f.flight_distance_km,
    vt.aircraft_name,
    vt.aircraft_code,
    vt.total_seats,
    f.status,
    COUNT(DISTINCT fc.id) AS flight_crew_count,
    COUNT(DISTINCT cc.id) AS cabin_crew_count,
    COUNT(DISTINCT p.id) AS passenger_count
FROM flights f
JOIN airlines a ON f.airline_id = a.id
JOIN airport_locations dep ON f.departure_airport_id = dep.id
JOIN airport_locations arr ON f.arrival_airport_id = arr.id
JOIN vehicle_types vt ON f.vehicle_type_id = vt.id
LEFT JOIN flight_crew fc ON f.id = fc.flight_id
LEFT JOIN cabin_crew cc ON f.id = cc.flight_id
LEFT JOIN passengers p ON f.id = p.flight_id
GROUP BY f.id, a.airline_name, a.airline_code, dep.airport_name, 
         dep.city, arr.airport_name, arr.city, vt.aircraft_name, 
         vt.aircraft_code, vt.total_seats;

-- ============================================================
-- SAMPLE DATA INSERT STATEMENTS
-- ============================================================

-- Insert sample airports
INSERT INTO airport_locations (airport_code, airport_name, city, country) VALUES
('JFK', 'John F. Kennedy International Airport', 'New York', 'USA'),
('LAX', 'Los Angeles International Airport', 'Los Angeles', 'USA'),
('LHR', 'London Heathrow Airport', 'London', 'United Kingdom'),
('CDG', 'Charles de Gaulle Airport', 'Paris', 'France'),
('IST', 'Istanbul Airport', 'Istanbul', 'Turkey');

-- Insert sample airlines
INSERT INTO airlines (airline_code, airline_name, country) VALUES
('OA', 'OpenAIrlines', 'International'),
('BA', 'British Airways', 'United Kingdom'),
('TK', 'Turkish Airlines', 'Turkey'),
('AA', 'American Airlines', 'USA'),
('AF', 'Air France', 'France');

-- Insert sample vehicle types with seating plans
INSERT INTO vehicle_types (aircraft_name, aircraft_code, total_seats, seating_plan, max_crew, max_passengers) VALUES
('Boeing 737-800', 'B738', 189, 
 '{"economy": 162, "business": 12, "firstClass": 8, "configuration": "3-3"}'::jsonb, 
 6, 189),
('Airbus A320', 'A320', 180, 
 '{"economy": 150, "business": 12, "firstClass": 8, "configuration": "3-3"}'::jsonb, 
 6, 180),
('Boeing 777-300ER', 'B77W', 396, 
 '{"economy": 340, "business": 28, "firstClass": 8, "configuration": "3-4-3"}'::jsonb, 
 10, 396);