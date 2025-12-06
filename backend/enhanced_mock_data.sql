-- Enhanced Mock Flight Data with Crew and Passenger Assignments
-- This builds on top of the existing mock_flight_data.sql
-- Run this AFTER running mock_flight_data.sql

-- First, let's add more diverse flights for better search/filter experience
INSERT INTO flights (flight_number, airline_id, departure_time, flight_duration_minutes, flight_distance_km, departure_airport_id, arrival_airport_id, vehicle_type_id, status) VALUES
-- Today's flights (November 28, 2025)
('AA2500', (SELECT id FROM airlines WHERE airline_code = 'AA'), '2025-11-28 06:30:00', 300, 3500, 
 (SELECT id FROM airport_locations WHERE airport_code = 'JFK'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'ORD'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'B738'), 'scheduled'),

('DL3100', (SELECT id FROM airlines WHERE airline_code = 'DL'), '2025-11-28 09:15:00', 420, 4800, 
 (SELECT id FROM airport_locations WHERE airport_code = 'ATL'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'LAX'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'B789'), 'scheduled'),

('BA9001', (SELECT id FROM airlines WHERE airline_code = 'BA'), '2025-11-28 14:00:00', 450, 5500, 
 (SELECT id FROM airport_locations WHERE airport_code = 'LHR'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'JFK'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'B77W'), 'boarding'),

('EK2020', (SELECT id FROM airlines WHERE airline_code = 'EK'), '2025-11-28 22:30:00', 500, 6200, 
 (SELECT id FROM airport_locations WHERE airport_code = 'DXB'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'SIN'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'A388'), 'scheduled'),

('LH5555', (SELECT id FROM airlines WHERE airline_code = 'LH'), '2025-11-28 11:45:00', 120, 900, 
 (SELECT id FROM airport_locations WHERE airport_code = 'FRA'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'CDG'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'A20N'), 'in-flight'),

-- Tomorrow's flights (November 29, 2025)
('UA7777', (SELECT id FROM airlines WHERE airline_code = 'UA'), '2025-11-29 08:00:00', 360, 4200, 
 (SELECT id FROM airport_locations WHERE airport_code = 'SFO'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'MIA'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'B738'), 'scheduled'),

('TK8888', (SELECT id FROM airlines WHERE airline_code = 'TK'), '2025-11-29 16:20:00', 240, 2500, 
 (SELECT id FROM airport_locations WHERE airport_code = 'IST'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'BCN'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'A20N'), 'scheduled'),

('AF1234', (SELECT id FROM airlines WHERE airline_code = 'AF'), '2025-11-29 12:30:00', 480, 5900, 
 (SELECT id FROM airport_locations WHERE airport_code = 'CDG'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'ATL'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'A359'), 'scheduled'),

('SQ9999', (SELECT id FROM airlines WHERE airline_code = 'SQ'), '2025-11-29 23:00:00', 780, 9500, 
 (SELECT id FROM airport_locations WHERE airport_code = 'SIN'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'LAX'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'A388'), 'scheduled'),

('KL4321', (SELECT id FROM airlines WHERE airline_code = 'KL'), '2025-11-29 10:15:00', 90, 650, 
 (SELECT id FROM airport_locations WHERE airport_code = 'AMS'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'FRA'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'A20N'), 'scheduled'),

-- Next week flights (December 1-3, 2025)
('AA3333', (SELECT id FROM airlines WHERE airline_code = 'AA'), '2025-12-01 15:00:00', 210, 2200, 
 (SELECT id FROM airport_locations WHERE airport_code = 'MIA'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'JFK'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'B738'), 'scheduled'),

('DL4444', (SELECT id FROM airlines WHERE airline_code = 'DL'), '2025-12-02 07:30:00', 180, 1600, 
 (SELECT id FROM airport_locations WHERE airport_code = 'SFO'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'LAX'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'A20N'), 'scheduled'),

('EK1111', (SELECT id FROM airlines WHERE airline_code = 'EK'), '2025-12-03 01:00:00', 420, 5100, 
 (SELECT id FROM airport_locations WHERE airport_code = 'DXB'), 
 (SELECT id FROM airport_locations WHERE airport_code = 'CDG'), 
 (SELECT id FROM vehicle_types WHERE aircraft_code = 'B77W'), 'scheduled');

-- Assign crew to some popular flights for demonstration
-- Assign crew to AA2500 (JFK to ORD)
UPDATE flight_crew SET flight_id = (SELECT id FROM flights WHERE flight_number = 'AA2500') 
WHERE employee_id IN ('FC001', 'FC002');

UPDATE cabin_crew SET flight_id = (SELECT id FROM flights WHERE flight_number = 'AA2500') 
WHERE employee_id IN ('CC001', 'CC002', 'CC003');

-- Assign crew to BA9001 (LHR to JFK)
UPDATE flight_crew SET flight_id = (SELECT id FROM flights WHERE flight_number = 'BA9001') 
WHERE employee_id IN ('FC007', 'FC008');

UPDATE cabin_crew SET flight_id = (SELECT id FROM flights WHERE flight_number = 'BA9001') 
WHERE employee_id IN ('CC006', 'CC007', 'CC008');

-- Assign crew to EK2020 (DXB to SIN)
UPDATE flight_crew SET flight_id = (SELECT id FROM flights WHERE flight_number = 'EK2020') 
WHERE employee_id IN ('FC003', 'FC006');

UPDATE cabin_crew SET flight_id = (SELECT id FROM flights WHERE flight_number = 'EK2020') 
WHERE employee_id IN ('CC004', 'CC005');

-- Add more passengers
INSERT INTO passengers (name, email, phone, passport_number) VALUES
('David Wilson', 'david.w@email.com', '+1-555-0201', 'P11111111'),
('Sarah Thompson', 'sarah.t@email.com', '+1-555-0202', 'P22222222'),
('Robert Johnson', 'robert.j@email.com', '+44-20-5550203', 'P33333333'),
('Jennifer Lee', 'jennifer.l@email.com', '+1-555-0204', 'P44444444'),
('Mohammed Khan', 'mohammed.k@email.com', '+971-4-5550205', 'P55555555'),
('Lisa Chen', 'lisa.c@email.com', '+65-6555-0206', 'P66666666'),
('Carlos Rodriguez', 'carlos.r@email.com', '+34-91-5550207', 'P77777777'),
('Anna Schmidt', 'anna.s@email.com', '+49-30-5550208', 'P88888888'),
('Yuki Tanaka', 'yuki.t@email.com', '+81-3-5550209', 'P99999999'),
('Marie Dupont', 'marie.d@email.com', '+33-1-5550210', 'P00000000'),
('Ahmed Ali', 'ahmed.ali@email.com', '+971-4-5550211', 'P10101010'),
('Sophie Brown', 'sophie.b@email.com', '+44-20-5550212', 'P20202020'),
('Lucas Silva', 'lucas.s@email.com', '+55-11-5550213', 'P30303030'),
('Emma Watson', 'emma.watson@email.com', '+44-20-5550214', 'P40404040'),
('Hans Mueller', 'hans.m@email.com', '+49-30-5550215', 'P50505050')
ON CONFLICT (passport_number) DO NOTHING;

-- Assign passengers to AA2500
UPDATE passengers SET flight_id = (SELECT id FROM flights WHERE flight_number = 'AA2500') 
WHERE passport_number IN ('P12345678', 'P23456789', 'P34567890', 'P11111111', 'P22222222');

-- Assign passengers to BA9001
UPDATE passengers SET flight_id = (SELECT id FROM flights WHERE flight_number = 'BA9001') 
WHERE passport_number IN ('P45678901', 'P56789012', 'P67890123', 'P33333333', 'P44444444', 'P40404040');

-- Assign passengers to EK2020
UPDATE passengers SET flight_id = (SELECT id FROM flights WHERE flight_number = 'EK2020') 
WHERE passport_number IN ('P78901234', 'P89012345', 'P55555555', 'P66666666', 'P10101010');

-- Assign passengers to DL3100
UPDATE passengers SET flight_id = (SELECT id FROM flights WHERE flight_number = 'DL3100') 
WHERE passport_number IN ('P90123456', 'P01234567', 'P77777777', 'P88888888');

-- Assign passengers to LH5555
UPDATE passengers SET flight_id = (SELECT id FROM flights WHERE flight_number = 'LH5555') 
WHERE passport_number IN ('P99999999', 'P00000000', 'P20202020', 'P50505050');

-- Add more flight crew for variety
INSERT INTO flight_crew (name, age, gender, nationality, employee_id, role, license_number, seniority_level, max_allowed_distance_km) VALUES
('Captain Isabella Martinez', 39, 'Female', 'Spain', 'FC009', 'Captain', 'ATP-112233', 'Senior', 15000),
('First Officer David Kim', 28, 'Male', 'South Korea', 'FC010', 'First Officer', 'CPL-445566', 'Junior', 8000),
('Captain Ahmed Hassan', 50, 'Male', 'UAE', 'FC011', 'Captain', 'ATP-778899', 'Senior', 15000),
('First Officer Maria Gonzalez', 31, 'Female', 'Mexico', 'FC012', 'First Officer', 'CPL-998877', 'Mid', 10000),
('Captain Rajesh Patel', 44, 'Male', 'India', 'FC013', 'Captain', 'ATP-556677', 'Senior', 15000),
('First Officer Sophie Dubois', 27, 'Female', 'France', 'FC014', 'First Officer', 'CPL-334455', 'Junior', 8000)
ON CONFLICT (employee_id) DO NOTHING;

-- Add more cabin crew
INSERT INTO cabin_crew (name, age, gender, nationality, employee_id, attendant_type, languages, recipes, vehicle_restrictions) VALUES
('Isabella Rodriguez', 29, 'Female', 'Spain', 'CC009', 'chief', '["Spanish", "English", "French"]', NULL, NULL),
('David Park', 26, 'Male', 'South Korea', 'CC010', 'regular', '["Korean", "English"]', NULL, NULL),
('Sarah Al-Mansouri', 33, 'Female', 'UAE', 'CC011', 'chef', '["Arabic", "English"]', 
 '["Machboos", "Hummus", "Shawarma", "Fattoush"]', NULL),
('Lucas Ferreira', 28, 'Male', 'Brazil', 'CC012', 'regular', '["Portuguese", "English", "Spanish"]', NULL, NULL),
('Nina Ivanova', 31, 'Female', 'Russia', 'CC013', 'chef', '["Russian", "English"]', 
 '["Beef Stroganoff", "Borscht", "Pelmeni"]', NULL),
('Omar Farah', 27, 'Male', 'Somalia', 'CC014', 'regular', '["Somali", "English", "Arabic"]', NULL, NULL),
('Priya Sharma', 30, 'Female', 'India', 'CC015', 'chief', '["Hindi", "English", "Gujarati"]', NULL, NULL),
('Jean-Pierre Martin', 34, 'Male', 'France', 'CC016', 'chef', '["French", "English", "Italian"]', 
 '["Bouillabaisse", "Cassoulet", "Crème Brûlée"]', NULL)
ON CONFLICT (employee_id) DO NOTHING;

-- Add pilot languages for new crew
INSERT INTO pilot_languages (pilot_id, language) VALUES
((SELECT id FROM flight_crew WHERE employee_id = 'FC009'), 'Spanish'),
((SELECT id FROM flight_crew WHERE employee_id = 'FC009'), 'English'),
((SELECT id FROM flight_crew WHERE employee_id = 'FC010'), 'Korean'),
((SELECT id FROM flight_crew WHERE employee_id = 'FC010'), 'English'),
((SELECT id FROM flight_crew WHERE employee_id = 'FC011'), 'Arabic'),
((SELECT id FROM flight_crew WHERE employee_id = 'FC011'), 'English'),
((SELECT id FROM flight_crew WHERE employee_id = 'FC012'), 'Spanish'),
((SELECT id FROM flight_crew WHERE employee_id = 'FC012'), 'English'),
((SELECT id FROM flight_crew WHERE employee_id = 'FC013'), 'Hindi'),
((SELECT id FROM flight_crew WHERE employee_id = 'FC013'), 'English'),
((SELECT id FROM flight_crew WHERE employee_id = 'FC014'), 'French'),
((SELECT id FROM flight_crew WHERE employee_id = 'FC014'), 'English')
ON CONFLICT DO NOTHING;

-- Summary: Quick reference for testing
-- Popular flight numbers to search:
-- Today (Nov 28): AA2500, DL3100, BA9001, EK2020, LH5555
-- Tomorrow (Nov 29): UA7777, TK8888, AF1234, SQ9999, KL4321
-- Next Week (Dec 1-3): AA3333, DL4444, EK1111
-- 
-- Popular routes:
-- JFK ↔ LAX, LHR, ORD
-- LHR ↔ JFK, CDG, AMS
-- DXB ↔ SIN, JFK, CDG
-- CDG ↔ JFK, BCN, FRA
--
-- Airlines with flights:
-- AA (American), DL (Delta), UA (United), BA (British Airways)
-- LH (Lufthansa), AF (Air France), EK (Emirates), TK (Turkish)
-- KL (KLM), SQ (Singapore)
