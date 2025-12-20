"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Plane } from "lucide-react";
import { useState } from "react";

interface PlaneViewProps {
  flight: any;
}

export function PlaneView({ flight }: PlaneViewProps) {
  const [hoveredSeat, setHoveredSeat] = useState<string | null>(null);

  const vehicleType = flight.vehicle_type || {};
  const seatingPlan = vehicleType.seating_plan || { rows: 30, seats_per_row: 10, business: 40, economy: 260 };
  const rows = seatingPlan.rows || 30;
  const seatsPerRow = seatingPlan.seats_per_row || 10;

  console.log('Vehicle type:', vehicleType);
  console.log('Seating plan:', seatingPlan);

  const seatMap = new Map<string, any>();

  const flightCrew = flight.flight_crew || [];
  const cabinCrew = flight.cabin_crew || [];
  const passengers = flight.passengers || [];

  console.log('=== PLANE VIEW DEBUG ===');
  console.log('Total passengers:', passengers.length);
  console.log('Flight Crew:', flightCrew.map((c: any) => ({ name: c.name, seat: c.seat_number })));
  console.log('Cabin Crew:', cabinCrew.map((c: any) => ({ name: c.name, seat: c.seat_number })));
  console.log('Passengers:', passengers.map((p: any) => ({ name: p.name, seat: p.seat_number })));
  console.log('First 5 passengers full data:', passengers.slice(0, 5));

  flightCrew.forEach((crew: any) => {
    if (crew.seat_number) {
      seatMap.set(crew.seat_number, { ...crew, type: "Flight Crew" });
    }
  });

  cabinCrew.forEach((crew: any) => {
    if (crew.seat_number) {
      seatMap.set(crew.seat_number, { ...crew, type: "Cabin Crew" });
    }
  });

  passengers.forEach((passenger: any) => {
    if (passenger.seat_number) {
      seatMap.set(passenger.seat_number, { ...passenger, type: "Passenger" });
    }
  });

  console.log('SeatMap contents:', Array.from(seatMap.entries()));
  console.log('SeatMap size:', seatMap.size);

  // Create crew display list with all crew members
  const crewDisplay: Array<{ seatLabel: string; person: any }> = [];
  
  // Add flight crew with seat assignments or auto-generated labels
  flightCrew.forEach((crew: any, index: number) => {
    const seatLabel = crew.seat_number || `FC${index + 1}`;
    crewDisplay.push({
      seatLabel,
      person: { ...crew, type: "Flight Crew" }
    });
  });
  
  // Add cabin crew with seat assignments or auto-generated labels
  cabinCrew.forEach((crew: any, index: number) => {
    const seatLabel = crew.seat_number || `CC${index + 1}`;
    crewDisplay.push({
      seatLabel,
      person: { ...crew, type: "Cabin Crew" }
    });
  });

  // Handle different seating plan structures
  let businessRows = 0;
  let economyRows = 0;

  if (seatingPlan.business_rows && Array.isArray(seatingPlan.business_rows)) {
    // New structure with business_rows and economy_rows arrays
    businessRows = seatingPlan.business_rows.length;
    economyRows = seatingPlan.economy_rows?.length || 0;
  } else if (seatingPlan.business && seatingPlan.economy) {
    // Old structure with business/economy seat counts
    businessRows = Math.ceil(seatingPlan.business / seatsPerRow);
    economyRows = rows - businessRows;
  }

  console.log('Plane configuration:', { rows, seatsPerRow, businessRows, economyRows });
  console.log('Sample seat labels that will be generated:');
  console.log('Row 1:', Array.from({ length: 6 }, (_, i) => `1${["A", "B", "C", "D", "E", "F"][i]}`));
  console.log('Row 2:', Array.from({ length: 6 }, (_, i) => `2${["A", "B", "C", "D", "E", "F"][i]}`));

  const generateSeatLabel = (row: number, seat: number): string => {
    const seatLetters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"];
    return `${row}${seatLetters[seat]}`;
  };

  const getSeatClass = (row: number): string => {
    return row <= businessRows ? "Business" : "Economy";
  };

  const getSeatColor = (seatLabel: string): string => {
    const person = seatMap.get(seatLabel);
    if (!person) return "bg-green-100 hover:bg-green-200 border-green-300";
    if (person.type === "Flight Crew") return "bg-blue-500 hover:bg-blue-600 border-blue-600 text-white";
    if (person.type === "Cabin Crew") return "bg-purple-500 hover:bg-purple-600 border-purple-600 text-white";
    return "bg-gray-400 hover:bg-gray-500 border-gray-500 text-white";
  };

  const renderSeatRow = (rowNumber: number, seatsInRow: number) => {
    const seats = [];
    const seatClass = getSeatClass(rowNumber);
    let renderedSeatsCount = 0;

    for (let i = 0; i < seatsInRow; i++) {
      const seatLabel = generateSeatLabel(rowNumber, i);
      const person = seatMap.get(seatLabel);

      // Skip crew seats - they're already shown in the crew area
      if (person && (person.type === "Flight Crew" || person.type === "Cabin Crew")) {
        continue;
      }

      // Add aisle space after half of the seats
      if (renderedSeatsCount === Math.floor(seatsInRow / 2)) {
        seats.push(
          <div key={`aisle-${rowNumber}-${i}`} className="w-6"></div>
        );
      }

      renderedSeatsCount++;

      seats.push(
        <div
          key={seatLabel}
          className={`relative w-10 h-10 border-2 rounded cursor-pointer transition-all ${getSeatColor(seatLabel)}`}
          onMouseEnter={() => setHoveredSeat(seatLabel)}
          onMouseLeave={() => setHoveredSeat(null)}
        >
          <div className="flex items-center justify-center h-full text-xs font-semibold">
            {seatLabel}
          </div>
          {hoveredSeat === seatLabel && person && (
            <div className="absolute z-50 left-0 bottom-full mb-2 bg-white border-2 border-gray-300 rounded-lg shadow-lg p-3 w-64 pointer-events-none">
              <div className="text-sm">
                <div className="font-semibold text-gray-900">{person.name}</div>
                <div className="text-gray-600 mt-1">
                  <div>Type: {person.type}</div>
                  <div>Age: {person.age}</div>
                  <div>Nationality: {person.nationality}</div>
                  {person.role && <div>Role: {person.role}</div>}
                  {person.attendant_type && <div>Type: {person.attendant_type}</div>}
                  {person.seat_type && <div>Class: {person.seat_type}</div>}
                </div>
              </div>
            </div>
          )}
        </div>
      );
    }

    return (
      <div key={rowNumber} className="flex items-center gap-2 mb-2">
        <div className="w-8 text-xs font-semibold text-gray-600">{rowNumber}</div>
        <div className="flex gap-1">{seats}</div>
        <Badge variant="outline" className="ml-2 text-xs">
          {seatClass}
        </Badge>
      </div>
    );
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Plane className="h-5 w-5" />
          Plane View - Seat Map
        </CardTitle>
        <CardDescription>
          {vehicleType.aircraft_name || 'Aircraft'} ({vehicleType.aircraft_code || 'N/A'}) - Hover over seats for details
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="mb-4 flex gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-green-100 border-2 border-green-300 rounded"></div>
            <span>Available</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-gray-400 border-2 border-gray-500 rounded"></div>
            <span>Passenger</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-blue-500 border-2 border-blue-600 rounded"></div>
            <span>Flight Crew</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-purple-500 border-2 border-purple-600 rounded"></div>
            <span>Cabin Crew</span>
          </div>
        </div>

        <div className="border rounded-lg p-6 bg-gray-50 overflow-x-auto">
          {/* Cockpit */}
          <div className="mb-4 text-center">
            <div className="inline-block bg-blue-600 text-white px-6 py-2 rounded-t-full font-semibold">
              COCKPIT
            </div>
          </div>

          {/* Crew seats */}
          <div className="mb-4 border-b pb-4">
            <div className="text-xs font-semibold text-gray-600 mb-2">CREW AREA</div>
            <div className="flex gap-2 flex-wrap">
              {crewDisplay.map(({ seatLabel, person }) => (
                <div
                  key={seatLabel}
                  className={`relative w-20 h-10 border-2 rounded cursor-pointer transition-all ${getSeatColor(seatLabel)} flex items-center justify-center`}
                  onMouseEnter={() => setHoveredSeat(seatLabel)}
                  onMouseLeave={() => setHoveredSeat(null)}
                >
                  <span className="text-xs font-semibold">{seatLabel}</span>
                  {hoveredSeat === seatLabel && (
                    <div className="absolute z-50 left-0 top-full mt-2 bg-white border-2 border-gray-300 rounded-lg shadow-lg p-3 w-64 pointer-events-none">
                      <div className="text-sm">
                        <div className="font-semibold text-gray-900">{person.name}</div>
                        <div className="text-gray-600 mt-1">
                          <div>Type: {person.type}</div>
                          <div>Age: {person.age}</div>
                          <div>Nationality: {person.nationality}</div>
                          {person.role && <div>Role: {person.role}</div>}
                          {person.attendant_type && <div>Type: {person.attendant_type}</div>}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Business Class */}
          {businessRows > 0 && (
            <div className="mb-4 border-b pb-4">
              <div className="text-xs font-semibold text-gray-600 mb-2">BUSINESS CLASS</div>
              {Array.from({ length: businessRows }, (_, i) => i + 1).map((row) =>
                renderSeatRow(row, 6)
              )}
            </div>
          )}

          <div>
            <div className="text-xs font-semibold text-gray-600 mb-2">ECONOMY CLASS</div>
            {Array.from({ length: economyRows }, (_, i) => i + businessRows + 1).map((row) =>
              renderSeatRow(row, 6)
            )}
            {economyRows > 10 && (
              <div className="text-center text-sm text-gray-500 mt-2">
                ... and {economyRows - 10} more rows
              </div>
            )}
          </div>
        </div>

        <div className="mt-4 text-sm text-gray-600">
          <div>Total Seats: {vehicleType.total_seats || 'N/A'}</div>
          <div>Occupied: {seatMap.size}</div>
          <div>Available: {(vehicleType.total_seats || 0) - seatMap.size}</div>
        </div>
      </CardContent>
    </Card>
  );
}