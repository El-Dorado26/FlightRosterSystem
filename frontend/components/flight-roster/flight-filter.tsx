"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Search, X } from "lucide-react";
import { Flight } from "@/lib/types";

interface FlightFilterProps {
  flights: Flight[];
  onFilter: (filteredFlights: Flight[]) => void;
}

export function FlightFilter({ flights, onFilter }: FlightFilterProps) {
  const [flightNumber, setFlightNumber] = useState("");
  const [selectedAirline, setSelectedAirline] = useState<string>("all");
  const [departureAirport, setDepartureAirport] = useState<string>("all");
  const [arrivalAirport, setArrivalAirport] = useState<string>("all");
  const [status, setStatus] = useState<string>("all");

  const uniqueAirlines = Array.from(
    new Map(flights.map(f => [f.airline.airline_code, f.airline])).values()
  );

  const uniqueAirports = Array.from(
    new Map(
      [
        ...flights.map(f => [f.departure_airport.airport_code, f.departure_airport] as const),
        ...flights.map(f => [f.arrival_airport.airport_code, f.arrival_airport] as const)
      ]
    ).values()
  );

  const handleFilter = () => {
    let filtered = [...flights];

    if (flightNumber) {
      filtered = filtered.filter((f) =>
        f.flight_number.toLowerCase().includes(flightNumber.toLowerCase())
      );
    }

    if (selectedAirline !== "all") {
      filtered = filtered.filter((f) => f.airline.airline_code === selectedAirline);
    }

    if (departureAirport !== "all") {
      filtered = filtered.filter((f) => f.departure_airport.airport_code === departureAirport);
    }

    if (arrivalAirport !== "all") {
      filtered = filtered.filter((f) => f.arrival_airport.airport_code === arrivalAirport);
    }

    if (status !== "all") {
      filtered = filtered.filter((f) => f.status.toLowerCase() === status.toLowerCase());
    }

    onFilter(filtered);
  };

  const handleReset = () => {
    setFlightNumber("");
    setSelectedAirline("all");
    setDepartureAirport("all");
    setArrivalAirport("all");
    setStatus("all");
    onFilter(flights);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Search className="h-5 w-5" />
          Search & Filter Flights
        </CardTitle>
        <CardDescription>Filter flights by various criteria</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <label className="text-sm font-medium mb-2 block">Flight Number</label>
          <Input
            placeholder="e.g., AA1234"
            value={flightNumber}
            onChange={(e) => setFlightNumber(e.target.value)}
          />
        </div>

        <div>
          <label className="text-sm font-medium mb-2 block">Airline</label>
          <Select value={selectedAirline} onValueChange={setSelectedAirline}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Airlines</SelectItem>
              {uniqueAirlines.map((airline) => (
                <SelectItem key={airline.id} value={airline.airline_code}>
                  {airline.airline_name} ({airline.airline_code})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div>
          <label className="text-sm font-medium mb-2 block">Departure Airport</label>
          <Select value={departureAirport} onValueChange={setDepartureAirport}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Airports</SelectItem>
              {uniqueAirports.map((airport) => (
                <SelectItem key={airport.id} value={airport.airport_code}>
                  {airport.airport_code} - {airport.city}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div>
          <label className="text-sm font-medium mb-2 block">Arrival Airport</label>
          <Select value={arrivalAirport} onValueChange={setArrivalAirport}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Airports</SelectItem>
              {uniqueAirports.map((airport) => (
                <SelectItem key={`arr-${airport.id}`} value={airport.airport_code}>
                  {airport.airport_code} - {airport.city}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div>
          <label className="text-sm font-medium mb-2 block">Status</label>
          <Select value={status} onValueChange={setStatus}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Statuses</SelectItem>
              <SelectItem value="scheduled">Scheduled</SelectItem>
              <SelectItem value="boarding">Boarding</SelectItem>
              <SelectItem value="departed">Departed</SelectItem>
              <SelectItem value="arrived">Arrived</SelectItem>
              <SelectItem value="cancelled">Cancelled</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="flex gap-2 pt-2">
          <Button onClick={handleFilter} className="flex-1">
            <Search className="h-4 w-4 mr-2" />
            Apply Filters
          </Button>
          <Button onClick={handleReset} variant="outline">
            <X className="h-4 w-4 mr-2" />
            Reset
          </Button>
        </div>

        <div className="text-xs text-muted-foreground text-center pt-2 border-t">
          Note: This is a mock filter. With backend integration, filters will query the Flight Information API.
        </div>
      </CardContent>
    </Card>
  );
}
