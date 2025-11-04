"use client";

import { Flight } from "@/lib/mock-data";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Plane, Calendar, Clock, MapPin } from "lucide-react";

interface FlightSelectorProps {
  flights: Flight[];
  selectedFlight: Flight | null;
  onFlightSelect: (flight: Flight) => void;
}

export function FlightSelector({ flights, selectedFlight, onFlightSelect }: FlightSelectorProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Plane className="h-5 w-5" />
          Select Flight
        </CardTitle>
        <CardDescription>Choose a flight to view roster details</CardDescription>
      </CardHeader>
      <CardContent>
        <Select
          value={selectedFlight?.id.toString()}
          onValueChange={(value) => {
            const flight = flights.find((f) => f.id.toString() === value);
            if (flight) onFlightSelect(flight);
          }}
        >
          <SelectTrigger className="w-full">
            <SelectValue placeholder="Select a flight" />
          </SelectTrigger>
          <SelectContent>
            {flights.map((flight) => (
              <SelectItem key={flight.id} value={flight.id.toString()}>
                <div className="flex items-center gap-2">
                  <span className="font-semibold">{flight.flight_number}</span>
                  <span className="text-muted-foreground">
                    {flight.departure_airport.airport_code} → {flight.arrival_airport.airport_code}
                  </span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        {selectedFlight && (
          <div className="mt-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Status:</span>
              <Badge variant={selectedFlight.status === "Scheduled" ? "default" : "secondary"}>
                {selectedFlight.status}
              </Badge>
            </div>

            <div className="flex items-start gap-2">
              <MapPin className="h-4 w-4 mt-0.5 text-muted-foreground" />
              <div className="flex-1 text-sm">
                <div className="font-medium">{selectedFlight.departure_airport.airport_name}</div>
                <div className="text-muted-foreground">
                  {selectedFlight.departure_airport.city}, {selectedFlight.departure_airport.country}
                </div>
              </div>
            </div>

            <div className="flex items-start gap-2">
              <MapPin className="h-4 w-4 mt-0.5 text-muted-foreground" />
              <div className="flex-1 text-sm">
                <div className="font-medium">{selectedFlight.arrival_airport.airport_name}</div>
                <div className="text-muted-foreground">
                  {selectedFlight.arrival_airport.city}, {selectedFlight.arrival_airport.country}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm">
                {new Date(selectedFlight.departure_time).toLocaleDateString("en-US", {
                  weekday: "short",
                  year: "numeric",
                  month: "short",
                  day: "numeric",
                })}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm">
                Duration: {Math.floor(selectedFlight.flight_duration_minutes / 60)}h{" "}
                {selectedFlight.flight_duration_minutes % 60}m
              </span>
            </div>

            <div className="pt-2 border-t">
              <div className="text-sm">
                <div className="flex justify-between mb-1">
                  <span className="text-muted-foreground">Aircraft:</span>
                  <span className="font-medium">{selectedFlight.vehicle_type.aircraft_name}</span>
                </div>
                <div className="flex justify-between mb-1">
                  <span className="text-muted-foreground">Distance:</span>
                  <span className="font-medium">{selectedFlight.flight_distance_km.toLocaleString()} km</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Airline:</span>
                  <span className="font-medium">{selectedFlight.airline.airline_name}</span>
                </div>
              </div>
            </div>

            {selectedFlight.shared_flight && (
              <div className="pt-2 border-t">
                <div className="text-xs font-semibold text-muted-foreground mb-1">SHARED FLIGHT</div>
                <div className="text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Partner:</span>
                    <span className="font-medium">{selectedFlight.shared_flight.secondary_airline.airline_name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Flight #:</span>
                    <span className="font-medium">{selectedFlight.shared_flight.secondary_flight_number}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
