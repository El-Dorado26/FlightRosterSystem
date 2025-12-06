-- Mock Flight Data for FlightRosterSystem
-- Run this after your database is initialized

-- Insert Airport Locations
INSERT INTO airport_locations (airport_code, airport_name, city, country) VALUES
('JFK', 'John F. Kennedy International Airport', 'New York', 'USA'),
('LAX', 'Los Angeles International Airport', 'Los Angeles', 'USA'),
('LHR', 'London Heathrow Airport', 'London', 'UK'),
('CDG', 'Charles de Gaulle Airport', 'Paris', 'France'),
('DXB', 'Dubai International Airport', 'Dubai', 'UAE'),
('NRT', 'Narita International Airport', 'Tokyo', 'Japan'),
('SIN', 'Singapore Changi Airport', 'Singapore', 'Singapore'),
('IST', 'Istanbul Airport', 'Istanbul', 'Turkey'),
('FRA', 'Frankfurt Airport', 'Frankfurt', 'Germany'),
('AMS', 'Amsterdam Schiphol Airport', 'Amsterdam', 'Netherlands'),
('ORD', 'O''Hare International Airport', 'Chicago', 'USA'),
('ATL', 'Hartsfield-Jackson Atlanta International Airport', 'Atlanta', 'USA'),
('SFO', 'San Francisco International Airport', 'San Francisco', 'USA'),
('MIA', 'Miami International Airport', 'Miami', 'USA'),
('BCN', 'Barcelona-El Prat Airport', 'Barcelona', 'Spain')
ON CONFLICT (airport_code) DO NOTHING;

-- Insert Airlines
INSERT INTO airlines (airline_code, airline_name, country) VALUES
('AA', 'American Airlines', 'USA'),
('DL', 'Delta Air Lines', 'USA'),
('UA', 'United Airlines', 'USA'),
('BA', 'British Airways', 'UK'),
('LH', 'Lufthansa', 'Germany'),
('AF', 'Air France', 'France'),
('EK', 'Emirates', 'UAE'),
('TK', 'Turkish Airlines', 'Turkey'),
('KL', 'KLM Royal Dutch Airlines', 'Netherlands'),
('SQ', 'Singapore Airlines', 'Singapore')
ON CONFLICT (airline_code) DO NOTHING;

-- Insert Vehicle Types
INSERT INTO vehicle_types (aircraft_name, aircraft_code, total_seats, seating_plan, max_crew, max_passengers) VALUES
('Boeing 737-800', 'B738', 189, 
 '{"economy": {"rows": 30, "seats_per_row": 6, "layout": "3-3"}, "business": {"rows": 2, "seats_per_row": 4, "layout": "2-2"}}', 
 8, 189),
('Airbus A320neo', 'A20N', 180, 
 '{"economy": {"rows": 28, "seats_per_row": 6, "layout": "3-3"}, "business": {"rows": 3, "seats_per_row": 4, "layout": "2-2"}}', 
 8, 180),
('Boeing 777-300ER', 'B77W', 396, 
 '{"economy": {"rows": 40, "seats_per_row": 9, "layout": "3-3-3"}, "business": {"rows": 8, "seats_per_row": 7, "layout": "2-3-2"}, "first": {"rows": 2, "seats_per_row": 4, "layout": "1-2-1"}}', 
 12, 396),
('Airbus A380-800', 'A388', 555, 
 '{"economy": {"rows": 60, "seats_per_row": 10, "layout": "3-4-3"}, "business": {"rows": 12, "seats_per_row": 7, "layout": "2-2-2"}, "first": {"rows": 3, "seats_per_row": 4, "layout": "1-2-1"}}', 
 18, 555),
('Boeing 787-9 Dreamliner', 'B789', 296, 
 '{"economy": {"rows": 32, "seats_per_row": 9, "layout": "3-3-3"}, "business": {"rows": 6, "seats_per_row": 7, "layout": "2-3-2"}}', 
 10, 296),
('Airbus A350-900', 'A359', 325, 
 '{"economy": {"rows": 35, "seats_per_row": 9, "layout": "3-3-3"}, "business": {"rows": 8, "seats_per_row": 6, "layout": "2-2-2"}}', 
 11, 325)
ON CONFLICT (aircraft_code) DO NOTHING;

-- Insert Flights (covering various dates, routes, and airlines)
-- December 2025 flights
INSERT INTO flights (flight_number, airline_id, departure_time, flight_duration_minutes, flight_distance_km, departure_airport_id, arrival_airport_id, vehicle_type_id, status) VALUES
-- American Airlines flights
('AA0100', (SELECT id FROM airlines WHERE airline_code = 'AA'), '2025-12-01 08:00:00', 360, 4000, 
 (SELECT id FROM airport_locations WHERE airport_code = 'JFK'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'LAX'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'B738'), 'scheduled'),

('AA0205', (SELECT id FROM airlines WHERE airline_code = 'AA'), '2025-12-01 14:30:00', 480, 5800, 
 (SELECT id FROM airport_locations WHERE airport_code = 'JFK'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'LHR'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'B77W'), 'scheduled'),

('AA0312', (SELECT id FROM airlines WHERE airline_code = 'AA'), '2025-12-02 10:15:00', 150, 1200, 
 (SELECT id FROM airport_locations WHERE airport_code = 'LAX'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'SFO'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'A20N'), 'scheduled'),

-- Delta Air Lines flights
('DL0088', (SELECT id FROM airlines WHERE airline_code = 'DL'), '2025-12-01 06:45:00', 540, 6900, 
 (SELECT id FROM airport_locations WHERE airport_code = 'ATL'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'CDG'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'A359'), 'scheduled'),

('DL0456', (SELECT id FROM airlines WHERE airline_code = 'DL'), '2025-12-02 16:20:00', 210, 1800, 
 (SELECT id FROM airport_locations WHERE airport_code = 'JFK'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'MIA'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'B738'), 'scheduled'),

('DL0789', (SELECT id FROM airlines WHERE airline_code = 'DL'), '2025-12-03 09:00:00', 600, 7500, 
 (SELECT id FROM airport_locations WHERE airport_code = 'ATL'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'NRT'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'B789'), 'scheduled'),

-- United Airlines flights
('UA0921', (SELECT id FROM airlines WHERE airline_code = 'UA'), '2025-12-01 12:30:00', 420, 5000, 
 (SELECT id FROM airport_locations WHERE airport_code = 'SFO'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'LHR'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'B77W'), 'scheduled'),

('UA1024', (SELECT id FROM airlines WHERE airline_code = 'UA'), '2025-12-02 07:15:00', 180, 1500, 
 (SELECT id FROM airport_locations WHERE airport_code = 'ORD'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'LAX'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'B738'), 'scheduled'),

('UA1567', (SELECT id FROM airlines WHERE airline_code = 'UA'), '2025-12-03 15:45:00', 660, 8200, 
 (SELECT id FROM airport_locations WHERE airport_code = 'SFO'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'SIN'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'B789'), 'scheduled'),

-- British Airways flights
('BA0112', (SELECT id FROM airlines WHERE airline_code = 'BA'), '2025-12-01 11:00:00', 480, 5550, 
 (SELECT id FROM airport_locations WHERE airport_code = 'LHR'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'JFK'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'A388'), 'scheduled'),

('BA0298', (SELECT id FROM airlines WHERE airline_code = 'BA'), '2025-12-02 18:30:00', 150, 1200, 
 (SELECT id FROM airport_locations WHERE airport_code = 'LHR'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'CDG'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'A20N'), 'scheduled'),

('BA0555', (SELECT id FROM airlines WHERE airline_code = 'BA'), '2025-12-04 08:20:00', 210, 1800, 
 (SELECT id FROM airport_locations WHERE airport_code = 'LHR'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'BCN'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'B738'), 'scheduled'),

-- Lufthansa flights
('LH0400', (SELECT id FROM airlines WHERE airline_code = 'LH'), '2025-12-01 13:15:00', 540, 6500, 
 (SELECT id FROM airport_locations WHERE airport_code = 'FRA'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'JFK'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'A359'), 'scheduled'),

('LH0902', (SELECT id FROM airlines WHERE airline_code = 'LH'), '2025-12-02 10:45:00', 90, 500, 
 (SELECT id FROM airport_locations WHERE airport_code = 'FRA'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'AMS'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'A20N'), 'scheduled'),

('LH0714', (SELECT id FROM airlines WHERE airline_code = 'LH'), '2025-12-03 19:30:00', 600, 7200, 
 (SELECT id FROM airport_locations WHERE airport_code = 'FRA'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'DXB'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'B77W'), 'scheduled'),

-- Emirates flights
('EK0001', (SELECT id FROM airlines WHERE airline_code = 'EK'), '2025-12-01 03:00:00', 840, 10500, 
 (SELECT id FROM airport_locations WHERE airport_code = 'DXB'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'JFK'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'A388'), 'scheduled'),

('EK0203', (SELECT id FROM airlines WHERE airline_code = 'EK'), '2025-12-02 08:45:00', 420, 5100, 
 (SELECT id FROM airport_locations WHERE airport_code = 'DXB'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'LHR'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'B77W'), 'scheduled'),

('EK0345', (SELECT id FROM airlines WHERE airline_code = 'EK'), '2025-12-03 23:30:00', 480, 5900, 
 (SELECT id FROM airport_locations WHERE airport_code = 'DXB'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'SIN'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'A388'), 'scheduled'),

-- Turkish Airlines flights
('TK0001', (SELECT id FROM airlines WHERE airline_code = 'TK'), '2025-12-01 01:30:00', 660, 8000, 
 (SELECT id FROM airport_locations WHERE airport_code = 'IST'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'JFK'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'B77W'), 'scheduled'),

('TK0123', (SELECT id FROM airlines WHERE airline_code = 'TK'), '2025-12-02 14:00:00', 240, 2400, 
 (SELECT id FROM airport_locations WHERE airport_code = 'IST'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'LHR'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'A20N'), 'scheduled'),

('TK0789', (SELECT id FROM airlines WHERE airline_code = 'TK'), '2025-12-04 05:15:00', 300, 3200, 
 (SELECT id FROM airport_locations WHERE airport_code = 'IST'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'FRA'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'B738'), 'scheduled'),

-- Air France flights
('AF0083', (SELECT id FROM airlines WHERE airline_code = 'AF'), '2025-12-01 10:20:00', 480, 5850, 
 (SELECT id FROM airport_locations WHERE airport_code = 'CDG'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'JFK'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'A359'), 'scheduled'),

('AF0456', (SELECT id FROM airlines WHERE airline_code = 'AF'), '2025-12-02 16:45:00', 120, 900, 
 (SELECT id FROM airport_locations WHERE airport_code = 'CDG'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'BCN'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'A20N'), 'scheduled'),

('AF0662', (SELECT id FROM airlines WHERE airline_code = 'AF'), '2025-12-03 22:00:00', 660, 8100, 
 (SELECT id FROM airport_locations WHERE airport_code = 'CDG'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'SIN'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'B77W'), 'scheduled'),

-- Singapore Airlines flights
('SQ0011', (SELECT id FROM airlines WHERE airline_code = 'SQ'), '2025-12-01 23:45:00', 1140, 14100, 
 (SELECT id FROM airport_locations WHERE airport_code = 'SIN'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'JFK'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'A388'), 'scheduled'),

('SQ0305', (SELECT id FROM airlines WHERE airline_code = 'SQ'), '2025-12-02 13:30:00', 420, 5100, 
 (SELECT id FROM airport_locations WHERE airport_code = 'SIN'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'NRT'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'B789'), 'scheduled'),

('SQ0634', (SELECT id FROM airlines WHERE airline_code = 'SQ'), '2025-12-03 20:15:00', 390, 4800, 
 (SELECT id FROM airport_locations WHERE airport_code = 'SIN'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'DXB'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'A359'), 'scheduled'),

-- KLM flights
('KL0641', (SELECT id FROM airlines WHERE airline_code = 'KL'), '2025-12-01 09:30:00', 510, 5900, 
 (SELECT id FROM airport_locations WHERE airport_code = 'AMS'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'JFK'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'B789'), 'scheduled'),

('KL1234', (SELECT id FROM airlines WHERE airline_code = 'KL'), '2025-12-02 12:00:00', 100, 750, 
 (SELECT id FROM airport_locations WHERE airport_code = 'AMS'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'LHR'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'A20N'), 'scheduled'),

('KL0809', (SELECT id FROM airlines WHERE airline_code = 'KL'), '2025-12-04 17:20:00', 180, 1500, 
 (SELECT id FROM airport_locations WHERE airport_code = 'AMS'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'BCN'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'B738'), 'scheduled'),

-- Additional flights for better testing (various dates in December)
('AA1500', (SELECT id FROM airlines WHERE airline_code = 'AA'), '2025-12-05 06:00:00', 240, 2400, 
 (SELECT id FROM airport_locations WHERE airport_code = 'ORD'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'JFK'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'B738'), 'scheduled'),

('DL2200', (SELECT id FROM airlines WHERE airline_code = 'DL'), '2025-12-06 14:30:00', 300, 3200, 
 (SELECT id FROM airport_locations WHERE airport_code = 'LAX'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'ATL'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'A20N'), 'scheduled'),

('UA3300', (SELECT id FROM airlines WHERE airline_code = 'UA'), '2025-12-07 11:45:00', 330, 3800, 
 (SELECT id FROM airport_locations WHERE airport_code = 'SFO'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'ORD'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'B789'), 'scheduled'),

('BA1800', (SELECT id FROM airlines WHERE airline_code = 'BA'), '2025-12-08 07:30:00', 180, 1400, 
 (SELECT id FROM airport_locations WHERE airport_code = 'LHR'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'AMS'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'A20N'), 'scheduled'),

('EK0777', (SELECT id FROM airlines WHERE airline_code = 'EK'), '2025-12-09 02:15:00', 720, 9000, 
 (SELECT id FROM airport_locations WHERE airport_code = 'DXB'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'LAX'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'A388'), 'scheduled'),

('LH1111', (SELECT id FROM airlines WHERE airline_code = 'LH'), '2025-12-10 15:00:00', 270, 2800, 
 (SELECT id FROM airport_locations WHERE airport_code = 'FRA'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'BCN'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'A20N'), 'scheduled');

-- Insert sample Flight Crew
INSERT INTO flight_crew (name, age, gender, nationality, employee_id, role, license_number, seniority_level, max_allowed_distance_km) VALUES
('Captain James Wilson', 45, 'Male', 'USA', 'FC001', 'Captain', 'ATP-001234', 'Senior', 15000),
('First Officer Sarah Chen', 32, 'Female', 'USA', 'FC002', 'First Officer', 'CPL-005678', 'Mid', 10000),
('Captain Mohammed Al-Rashid', 52, 'Male', 'UAE', 'FC003', 'Captain', 'ATP-009876', 'Senior', 15000),
('First Officer Emily Rodriguez', 29, 'Female', 'Spain', 'FC004', 'First Officer', 'CPL-011223', 'Junior', 8000),
('Captain Hans Mueller', 48, 'Male', 'Germany', 'FC005', 'Captain', 'ATP-445566', 'Senior', 15000),
('First Officer Akira Tanaka', 35, 'Male', 'Japan', 'FC006', 'First Officer', 'CPL-778899', 'Mid', 10000),
('Captain Elizabeth Brown', 41, 'Female', 'UK', 'FC007', 'Captain', 'ATP-332211', 'Senior', 15000),
('First Officer Pierre Dubois', 30, 'Male', 'France', 'FC008', 'First Officer', 'CPL-665544', 'Mid', 10000)
ON CONFLICT (employee_id) DO NOTHING;

-- Insert sample Cabin Crew
INSERT INTO cabin_crew (name, age, gender, nationality, employee_id, attendant_type, languages, recipes, vehicle_restrictions) VALUES
('Maria Santos', 28, 'Female', 'Philippines', 'CC001', 'chief', '["English", "Tagalog", "Spanish"]', NULL, NULL),
('Ahmed Hassan', 32, 'Male', 'Egypt', 'CC002', 'regular', '["English", "Arabic"]', NULL, NULL),
('Sophie Martin', 26, 'Female', 'France', 'CC003', 'chef', '["French", "English"]', 
 '["Coq au Vin", "Beef Bourguignon", "Ratatouille"]', NULL),
('Li Wei', 30, 'Female', 'China', 'CC004', 'regular', '["Mandarin", "English"]', NULL, NULL),
('Marco Rossi', 35, 'Male', 'Italy', 'CC005', 'chef', '["Italian", "English"]', 
 '["Risotto Milanese", "Osso Buco", "Tiramisu", "Pasta Carbonara"]', NULL),
('Anna Kowalski', 27, 'Female', 'Poland', 'CC006', 'chief', '["Polish", "English", "German"]', NULL, NULL),
('Carlos Mendez', 29, 'Male', 'Mexico', 'CC007', 'regular', '["Spanish", "English"]', NULL, NULL),
('Yuki Yamamoto', 31, 'Female', 'Japan', 'CC008', 'chef', '["Japanese", "English"]', 
 '["Sushi Selection", "Teriyaki Chicken", "Miso Soup"]', NULL)
ON CONFLICT (employee_id) DO NOTHING;

-- Insert sample Passengers
INSERT INTO passengers (name, email, phone, passport_number) VALUES
('John Smith', 'john.smith@email.com', '+1-555-0101', 'P12345678'),
('Emma Johnson', 'emma.j@email.com', '+1-555-0102', 'P23456789'),
('Michael Brown', 'm.brown@email.com', '+44-20-5550103', 'P34567890'),
('Olivia Davis', 'olivia.d@email.com', '+1-555-0104', 'P45678901'),
('William Garcia', 'will.garcia@email.com', '+34-91-5550105', 'P56789012'),
('Sophia Martinez', 'sophia.m@email.com', '+1-555-0106', 'P67890123'),
('James Anderson', 'j.anderson@email.com', '+1-555-0107', 'P78901234'),
('Isabella Taylor', 'bella.t@email.com', '+49-30-5550108', 'P89012345'),
('Alexander White', 'alex.white@email.com', '+1-555-0109', 'P90123456'),
('Mia Thompson', 'mia.t@email.com', '+33-1-5550110', 'P01234567')
ON CONFLICT (passport_number) DO NOTHING;

-- Insert sample Pilot Languages
INSERT INTO pilot_languages (pilot_id, language) VALUES
((SELECT id FROM flight_crew WHERE employee_id = 'FC001'), 'English'),
((SELECT id FROM flight_crew WHERE employee_id = 'FC001'), 'Spanish'),
((SELECT id FROM flight_crew WHERE employee_id = 'FC002'), 'English'),
((SELECT id FROM flight_crew WHERE employee_id = 'FC002'), 'Mandarin'),
((SELECT id FROM flight_crew WHERE employee_id = 'FC003'), 'Arabic'),
((SELECT id FROM flight_crew WHERE employee_id = 'FC003'), 'English'),
((SELECT id FROM flight_crew WHERE employee_id = 'FC004'), 'Spanish'),
((SELECT id FROM flight_crew WHERE employee_id = 'FC004'), 'English'),
((SELECT id FROM flight_crew WHERE employee_id = 'FC005'), 'German'),
((SELECT id FROM flight_crew WHERE employee_id = 'FC005'), 'English'),
((SELECT id FROM flight_crew WHERE employee_id = 'FC006'), 'Japanese'),
((SELECT id FROM flight_crew WHERE employee_id = 'FC006'), 'English'),
((SELECT id FROM flight_crew WHERE employee_id = 'FC007'), 'English'),
((SELECT id FROM flight_crew WHERE employee_id = 'FC008'), 'French'),
((SELECT id FROM flight_crew WHERE employee_id = 'FC008'), 'English')
ON CONFLICT DO NOTHING;

-- Note: The flights are created without assigned crew/passengers initially
-- This allows you to test the crew assignment and passenger booking features
-- You can later update flights to assign crew and passengers as needed
