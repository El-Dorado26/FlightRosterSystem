"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Plane, Search, AlertCircle, CheckCircle2, Users, X } from "lucide-react";

interface SeatAssignmentProps {
  flight: any;
  onSeatsAssigned: (assignments: { [passengerId: number]: string }) => void;
  initialAssignments?: { [passengerId: number]: string };
}

interface SeatOccupancy {   
  passengerId: number;
  passengerName: string;
  type: 'passenger' | 'flight_crew' | 'cabin_crew';
}

export function SeatAssignment({ flight, onSeatsAssigned, initialAssignments = {} }: SeatAssignmentProps) {
  const [seatAssignments, setSeatAssignments] = useState<{ [passengerId: number]: string }>(initialAssignments);
  const [seatOccupancy, setSeatOccupancy] = useState<Map<string, SeatOccupancy>>(new Map());
  const [selectedPassenger, setSelectedPassenger] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [hoveredSeat, setHoveredSeat] = useState<string | null>(null);
  const [errors, setErrors] = useState<string[]>([]);

  const vehicleType = flight?.vehicle_type || {};
  const seatingPlan = vehicleType.seating_plan || { rows: 30, seats_per_row: 6, business: 24, economy: 156 };
  const rows = seatingPlan.rows || 30;
  const seatsPerRow = seatingPlan.seats_per_row || 6;

  const passengers = flight?.passengers || [];
  const flightCrew = flight?.flight_crew || [];
  const cabinCrew = flight?.cabin_crew || [];

  // Filter passengers (infants don't need seats)
  const assignablePassengers = passengers.filter((p: any) => !p.parent_id);
  const infantsWithParents = passengers.filter((p: any) => p.parent_id);

  useEffect(() => {
    buildOccupancyMap();
    validateAssignments();
  }, [flight, seatAssignments]);

  useEffect(() => {
    onSeatsAssigned(seatAssignments);
  }, [seatAssignments]);

  const buildOccupancyMap = () => {
    const occupancy = new Map<string, SeatOccupancy>();

    // Add existing passenger seat assignments
    passengers.forEach((p: any) => {
      if (p.seat_number && !p.parent_id) {
        occupancy.set(p.seat_number, {
          passengerId: p.id,
          passengerName: p.name,
          type: 'passenger'
        });
      }
    });

    // Add flight crew seats
    flightCrew.forEach((c: any) => {
      if (c.seat_number) {
        occupancy.set(c.seat_number, {
          passengerId: c.id,
          passengerName: c.name,
          type: 'flight_crew'
        });
      }
    });

    // Add cabin crew seats
    cabinCrew.forEach((c: any) => {
      if (c.seat_number) {
        occupancy.set(c.seat_number, {
          passengerId: c.id,
          passengerName: c.name,
          type: 'cabin_crew'
        });
      }
    });

    // Add new assignments from state
    Object.entries(seatAssignments).forEach(([passengerId, seatNumber]) => {
      const passenger = passengers.find((p: any) => p.id === parseInt(passengerId));
      if (passenger) {
        occupancy.set(seatNumber, {
          passengerId: passenger.id,
          passengerName: passenger.name,
          type: 'passenger'
        });
      }
    });

    setSeatOccupancy(occupancy);
  };

  const validateAssignments = () => {
    const newErrors: string[] = [];
    const assignedSeats = new Set<string>();

    // Check for duplicate assignments
    Object.values(seatAssignments).forEach(seat => {
      if (assignedSeats.has(seat)) {
        newErrors.push(`Duplicate seat assignment: ${seat}`);
      }
      assignedSeats.add(seat);
    });

    // Check if all passengers have seats
    const unassigned = assignablePassengers.filter(
      (p: any) => !p.seat_number && !seatAssignments[p.id]
    );
    if (unassigned.length > 0) {
      newErrors.push(`${unassigned.length} passenger(s) without seats`);
    }

    setErrors(newErrors);
  };

  const generateSeatLabel = (row: number, seat: number): string => {
    const seatLetters = ["A", "B", "C", "D", "E", "F", "G", "H", "I"];
    return `${row}${seatLetters[seat]}`;
  };

  const getSeatClass = (row: number): string => {
    const businessRows = Math.ceil(seatingPlan.business / seatsPerRow);
    return row <= businessRows ? "Business" : "Economy";
  };

  const isSeatAvailable = (seatLabel: string): boolean => {
    return !seatOccupancy.has(seatLabel);
  };

  const getSeatColor = (seatLabel: string): string => {
    const occupant = seatOccupancy.get(seatLabel);
    if (!occupant) return "bg-green-100 hover:bg-green-200 border-green-300";
    if (occupant.type === 'flight_crew') return "bg-blue-500 border-blue-600 text-white cursor-not-allowed";
    if (occupant.type === 'cabin_crew') return "bg-purple-500 border-purple-600 text-white cursor-not-allowed";
    
    // Check if this is a newly assigned seat
    const isNewAssignment = Object.values(seatAssignments).includes(seatLabel);
    if (isNewAssignment) return "bg-yellow-400 hover:bg-yellow-500 border-yellow-600 text-white";
    
    return "bg-gray-400 border-gray-500 text-white cursor-not-allowed";
  };

  const handleSeatClick = (seatLabel: string) => {
    if (!selectedPassenger) {
      // Show alert to select passenger first
      return;
    }

    const occupant = seatOccupancy.get(seatLabel);
    
    // Can't assign to crew seats
    if (occupant && (occupant.type === 'flight_crew' || occupant.type === 'cabin_crew')) {
      return;
    }

    // If seat is occupied by another passenger, unassign them first
    if (occupant && occupant.type === 'passenger' && occupant.passengerId !== selectedPassenger) {
      return;
    }

    // Assign seat
    setSeatAssignments(prev => ({
      ...prev,
      [selectedPassenger]: seatLabel
    }));

    // Clear selection after assignment
    setSelectedPassenger(null);
  };

  const handleRemoveSeat = (passengerId: number) => {
    setSeatAssignments(prev => {
      const newAssignments = { ...prev };
      delete newAssignments[passengerId];
      return newAssignments;
    });
  };

  const filteredPassengers = assignablePassengers.filter((p: any) => 
    p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.passport_number.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const assignedPassengerIds = new Set([
    ...passengers.filter((p: any) => p.seat_number && !p.parent_id).map((p: any) => p.id),
    ...Object.keys(seatAssignments).map(id => parseInt(id))
  ]);

  const unassignedPassengers = filteredPassengers.filter((p: any) => !assignedPassengerIds.has(p.id));

  const renderSeatRow = (rowNumber: number, seatsInRow: number) => {
    const seats = [];
    const seatClass = getSeatClass(rowNumber);

    for (let i = 0; i < seatsInRow; i++) {
      const seatLabel = generateSeatLabel(rowNumber, i);
      const occupant = seatOccupancy.get(seatLabel);
      const isAvailable = isSeatAvailable(seatLabel);

      // Add aisle space
      if (i === Math.floor(seatsInRow / 2)) {
        seats.push(
          <div key={`aisle-${rowNumber}-${i}`} className="w-6"></div>
        );
      }

      seats.push(
        <div
          key={seatLabel}
          className={`relative w-10 h-10 border-2 rounded cursor-pointer transition-all ${getSeatColor(seatLabel)} ${
            selectedPassenger && isAvailable ? 'ring-2 ring-blue-400' : ''
          }`}
          onClick={() => handleSeatClick(seatLabel)}
          onMouseEnter={() => setHoveredSeat(seatLabel)}
          onMouseLeave={() => setHoveredSeat(null)}
        >
          <div className="flex items-center justify-center h-full text-xs font-semibold">
            {seatLabel}
          </div>
          {hoveredSeat === seatLabel && occupant && (
            <div className="absolute z-50 left-1/2 transform -translate-x-1/2 bottom-full mb-2 bg-white border-2 border-gray-300 rounded-lg shadow-lg p-3 w-48 pointer-events-none">
              <div className="text-sm text-gray-900">
                <div className="font-semibold">{occupant.passengerName}</div>
                <div className="text-gray-600">
                  {occupant.type === 'flight_crew' && 'Flight Crew'}
                  {occupant.type === 'cabin_crew' && 'Cabin Crew'}
                  {occupant.type === 'passenger' && 'Passenger'}
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
    <div className="grid grid-cols-3 gap-4">
      {/* Left Column: Seat Map */}
      <div className="col-span-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Plane className="h-5 w-5" />
              Interactive Seat Map
            </CardTitle>
            <CardDescription>
              {selectedPassenger 
                ? "Click a green seat to assign" 
                : "Select a passenger from the list, then click a seat"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="mb-4 flex gap-4 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 bg-green-100 border-2 border-green-300 rounded"></div>
                <span>Available</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 bg-yellow-400 border-2 border-yellow-600 rounded"></div>
                <span>New Assignment</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 bg-gray-400 border-2 border-gray-500 rounded"></div>
                <span>Occupied</span>
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

            <div className="max-h-96 overflow-y-auto border rounded-lg p-4 bg-gray-50">
              {Array.from({ length: rows }, (_, i) => i + 1).map(row => 
                renderSeatRow(row, seatsPerRow)
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Right Column: Passenger List */}
      <div className="space-y-4">
        {/* Validation Status */}
        {errors.length > 0 ? (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              <div className="text-sm space-y-1">
                {errors.map((error, idx) => (
                  <div key={idx}>• {error}</div>
                ))}
              </div>
            </AlertDescription>
          </Alert>
        ) : (
          <Alert className="border-green-200 bg-green-50">
            <CheckCircle2 className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800 text-sm">
              All passengers assigned!
            </AlertDescription>
          </Alert>
        )}

        {/* Statistics */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Assignment Progress</CardTitle>
          </CardHeader>
          <CardContent className="text-sm space-y-2">
            <div className="flex justify-between">
              <span>Total Passengers:</span>
              <strong>{assignablePassengers.length}</strong>
            </div>
            <div className="flex justify-between">
              <span>Assigned:</span>
              <strong>{assignedPassengerIds.size}</strong>
            </div>
            <div className="flex justify-between">
              <span>Unassigned:</span>
              <strong>{unassignedPassengers.length}</strong>
            </div>
            {infantsWithParents.length > 0 && (
              <div className="flex justify-between text-gray-600">
                <span>Infants (no seat):</span>
                <strong>{infantsWithParents.length}</strong>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Passenger List */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <Users className="h-4 w-4" />
              Unassigned Passengers
            </CardTitle>
            <div className="relative">
              <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search passengers..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8 text-sm"
              />
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <div className="max-h-96 overflow-y-auto">
              {unassignedPassengers.length === 0 ? (
                <div className="p-4 text-center text-sm text-gray-500">
                  All passengers have been assigned seats
                </div>
              ) : (
                <div className="space-y-1">
                  {unassignedPassengers.map((passenger: any) => (
                    <div
                      key={passenger.id}
                      onClick={() => setSelectedPassenger(passenger.id)}
                      className={`p-3 border-b cursor-pointer transition-colors ${
                        selectedPassenger === passenger.id
                          ? 'bg-blue-100 border-blue-300'
                          : 'hover:bg-gray-50'
                      }`}
                    >
                      <div className="font-medium text-sm">{passenger.name}</div>
                      <div className="text-xs text-gray-600">
                        {passenger.passport_number}
                        {passenger.seat_type && ` • ${passenger.seat_type}`}
                        {passenger.class && ` • ${passenger.class}`}
                      </div>
                      {seatAssignments[passenger.id] && (
                        <Badge variant="secondary" className="mt-1 text-xs">
                          {seatAssignments[passenger.id]}
                        </Badge>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Currently Assigned (with option to remove) */}
        {Object.keys(seatAssignments).length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">New Assignments</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="max-h-48 overflow-y-auto">
                {Object.entries(seatAssignments).map(([passengerId, seatNumber]) => {
                  const passenger = passengers.find((p: any) => p.id === parseInt(passengerId));
                  if (!passenger) return null;
                  return (
                    <div key={passengerId} className="flex items-center justify-between p-2 border-b text-sm">
                      <div>
                        <div className="font-medium">{passenger.name}</div>
                        <Badge variant="secondary" className="text-xs">{seatNumber}</Badge>
                      </div>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleRemoveSeat(parseInt(passengerId))}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
