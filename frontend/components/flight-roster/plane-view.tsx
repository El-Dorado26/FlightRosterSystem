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
  const seatingPlan = vehicleType.seating_plan || { rows: 30, seats_per_row: 6, business: 24, economy: 156 };
  const rows = seatingPlan.rows || 30;
  const seatsPerRow = seatingPlan.seats_per_row || 6;

  const seatMap = new Map<string, any>();

  const flightCrew = flight.flight_crew || [];
  const cabinCrew = flight.cabin_crew || [];
  const passengers = flight.passengers || [];

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

  // Generate seat grid
  const businessRows = Math.ceil(seatingPlan.business / 6); // Assuming 6 seats per business row
  const economyRows = rows - businessRows;

  const generateSeatLabel = (row: number, seat: number): string => {
    const seatLetters = ["A", "B", "C", "D", "E", "F", "G", "H", "I"];
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

    for (let i = 0; i < seatsInRow; i++) {
      const seatLabel = generateSeatLabel(rowNumber, i);
      const person = seatMap.get(seatLabel);

      // Add aisle space
      if (i === Math.floor(seatsInRow / 2)) {
        seats.push(
          <div key={`aisle-${rowNumber}-${i}`} className="w-6"></div>
        );
      }

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
            <div className="absolute z-50 left-1/2 transform -translate-x-1/2 bottom-full mb-2 bg-white border-2 border-gray-300 rounded-lg shadow-lg p-3 w-64 pointer-events-none">
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
              {Array.from(seatMap.entries())
                .filter(([_, person]) => person.type === "Flight Crew" || person.type === "Cabin Crew")
                .map(([seatLabel, person]) => (
                  <div
                    key={seatLabel}
                    className={`relative w-20 h-10 border-2 rounded cursor-pointer transition-all ${getSeatColor(seatLabel)} flex items-center justify-center`}
                    onMouseEnter={() => setHoveredSeat(seatLabel)}
                    onMouseLeave={() => setHoveredSeat(null)}
                  >
                    <span className="text-xs font-semibold">{seatLabel}</span>
                    {hoveredSeat === seatLabel && (
                      <div className="absolute z-50 left-1/2 transform -translate-x-1/2 bottom-full mb-2 bg-white border-2 border-gray-300 rounded-lg shadow-lg p-3 w-64 pointer-events-none">
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
                renderSeatRow(row, Math.min(6, seatsPerRow))
              )}
            </div>
          )}

          {/* Economy Class - Showing first 10 rows as sample */}
          <div>
            <div className="text-xs font-semibold text-gray-600 mb-2">ECONOMY CLASS</div>
            {Array.from({ length: Math.min(10, economyRows) }, (_, i) => i + businessRows + 1).map((row) =>
              renderSeatRow(row, seatsPerRow)
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