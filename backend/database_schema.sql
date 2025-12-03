-- ============================================================
-- TABLE: airports
-- ============================================================
CREATE TABLE airports (
    id SERIAL PRIMARY KEY,
    airport_code VARCHAR(3) UNIQUE NOT NULL,
    airport_name VARCHAR(255) NOT NULL,
    city VARCHAR(255) NOT NULL,
    country VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_airport_code ON airports(airport_code);

-- ============================================================
-- TABLE: vehicle_types
-- Aircraft types with seating configuration AND menu
-- ============================================================
CREATE TABLE vehicle_types (
    id SERIAL PRIMARY KEY,
    aircraft_name VARCHAR(255) UNIQUE NOT NULL,
    aircraft_code VARCHAR(10) UNIQUE NOT NULL,
    total_seats INT NOT NULL,
    seating_plan JSONB NOT NULL,
    max_crew INT NOT NULL,
    max_passengers INT NOT NULL,
    menu_items JSONB,
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
    home_airport_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (home_airport_id) REFERENCES airports(id) ON DELETE SET NULL
);

CREATE INDEX idx_airline_home_airport ON airlines(home_airport_id);

-- ============================================================
-- TABLE: flights
-- Main flights table with shared/connecting flight info as JSONB
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
    shared_flight_info JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (airline_id) REFERENCES airlines(id) ON DELETE CASCADE,
    FOREIGN KEY (departure_airport_id) REFERENCES airports(id) ON DELETE CASCADE,
    FOREIGN KEY (arrival_airport_id) REFERENCES airports(id) ON DELETE CASCADE,
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
-- TABLE: flight_crew
-- Pilots and technical crew with airline employment
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
    allowed_vehicle_types JSONB,
    airline_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    flight_id INT,
    FOREIGN KEY (flight_id) REFERENCES flights(id) ON DELETE SET NULL,
    FOREIGN KEY (airline_id) REFERENCES airlines(id) ON DELETE SET NULL
);

CREATE INDEX idx_employee_id ON flight_crew(employee_id);
CREATE INDEX idx_seniority ON flight_crew(seniority_level);
CREATE INDEX idx_crew_airline ON flight_crew(airline_id);

-- ============================================================
-- TABLE: cabin_crew
-- Flight attendants with airline employment
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
    allowed_vehicle_types JSONB,
    airline_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    flight_id INT,
    FOREIGN KEY (flight_id) REFERENCES flights(id) ON DELETE SET NULL,
    FOREIGN KEY (airline_id) REFERENCES airlines(id) ON DELETE SET NULL
);

CREATE INDEX idx_crew_employee_id ON cabin_crew(employee_id);
CREATE INDEX idx_crew_role ON cabin_crew(role);
CREATE INDEX idx_cabin_crew_airline ON cabin_crew(airline_id);

-- ============================================================
-- TABLE: passengers
-- Passenger information with affiliations as JSONB
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
    affiliated_passenger_ids JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    flight_id INT,
    FOREIGN KEY (flight_id) REFERENCES flights(id) ON DELETE SET NULL,
    FOREIGN KEY (parent_id) REFERENCES passengers(id) ON DELETE SET NULL
);

CREATE INDEX idx_email ON passengers(email);
CREATE INDEX idx_passport ON passengers(passport_number);
CREATE INDEX idx_flight_seat ON passengers(flight_id, seat_number);

-- ============================================================
-- SAMPLE DATA
-- ============================================================

INSERT INTO airports (airport_code, airport_name, city, country) VALUES
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

INSERT INTO vehicle_types (aircraft_name, aircraft_code, total_seats, seating_plan, max_crew, max_passengers, menu_items) VALUES
('Boeing 737-800', 'B738', 189, 
 '{"economy": 162, "business": 12, "firstClass": 8, "configuration": "3-3"}'::jsonb, 
 6, 189,
 '["Chicken", "Beef", "Vegetarian", "Snacks", "Beverages"]'::jsonb),
('Airbus A320', 'A320', 180, 
 '{"economy": 150, "business": 12, "firstClass": 8, "configuration": "3-3"}'::jsonb, 
 6, 180,
 '["Fish", "Pasta", "Vegan", "Snacks", "Beverages"]'::jsonb),
('Boeing 777-300ER', 'B77W', 396, 
 '{"economy": 340, "business": 28, "firstClass": 8, "configuration": "3-4-3"}'::jsonb, 
 10, 396,
 '["Premium Steak", "Salmon", "Vegetarian Deluxe", "Desserts", "Premium Beverages"]'::jsonb);

-- ============================================================
-- END OF SCHEMA
-- ============================================================

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