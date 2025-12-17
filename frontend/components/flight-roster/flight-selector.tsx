"use client";

import { useState, useRef, useEffect } from "react";
import { Flight } from "@/lib/mock-data";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Plane, Calendar, Clock, MapPin, Loader2, Search, X } from "lucide-react";

interface FlightSelectorProps {
  flights: Flight[];
  selectedFlight: Flight | null;
  onFlightSelect: (flight: Flight) => void;
  isLoading?: boolean;
}

export function FlightSelector({ flights, selectedFlight, onFlightSelect, isLoading = false }: FlightSelectorProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  
  const filteredFlights = flights.filter((flight) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      flight.flight_number.toLowerCase().includes(query) ||
      flight.departure_airport.airport_code.toLowerCase().includes(query) ||
      flight.arrival_airport.airport_code.toLowerCase().includes(query) ||
      flight.departure_airport.city.toLowerCase().includes(query) ||
      flight.arrival_airport.city.toLowerCase().includes(query) ||
      flight.airline.airline_name.toLowerCase().includes(query)
    );
  });

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleFlightClick = (flight: Flight) => {
    onFlightSelect(flight);
    setSearchQuery("");
    setShowDropdown(false);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Plane className="h-5 w-5" />
          Select Flight
        </CardTitle>
        <CardDescription>
          {searchQuery 
            ? `${filteredFlights.length} flight${filteredFlights.length !== 1 ? 's' : ''} found`
            : 'Choose a flight to view roster details'
          }
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="relative" ref={dropdownRef}>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              type="text"
              placeholder="Search flights..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setShowDropdown(true);
              }}
              onFocus={() => setShowDropdown(true)}
              className="pl-10 pr-10"
            />
            {searchQuery && (
              <button
                onClick={() => {
                  setSearchQuery("");
                  setShowDropdown(false);
                }}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>
          
          {showDropdown && (
            <div className="absolute z-50 w-full mt-1 bg-white border rounded-lg shadow-lg max-h-80 overflow-y-auto">
              {filteredFlights.length === 0 ? (
                <div className="px-4 py-8 text-center text-sm text-gray-500">
                  No flights match your search
                </div>
              ) : (
                <div className="py-1">
                  {filteredFlights.map((flight) => (
                    <button
                      key={flight.id}
                      onClick={() => handleFlightClick(flight)}
                      className="w-full px-4 py-3 text-left hover:bg-gray-50 border-b last:border-b-0 transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-semibold text-gray-900">{flight.flight_number}</div>
                          <div className="text-sm text-gray-600">
                            {flight.departure_airport.airport_code} → {flight.arrival_airport.airport_code}
                          </div>
                        </div>
                        <div className="text-right text-xs text-gray-500">
                          <div>{flight.airline.airline_name}</div>
                          <div>{new Date(flight.departure_time).toLocaleDateString()}</div>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {selectedFlight && (
          <div className="mt-4 space-y-3">
            {isLoading && (
              <div className="flex items-center gap-2 text-sm text-blue-600 bg-blue-50 px-3 py-2 rounded-md">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Loading flight details...</span>
              </div>
            )}
            
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-3">
              <div className="text-xs text-blue-600 font-semibold mb-1">SELECTED FLIGHT</div>
              <div className="text-2xl font-bold text-blue-900">{selectedFlight.flight_number}</div>
            </div>
            
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

            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm">
                Arrival: {selectedFlight.arrival_time ? new Date(selectedFlight.arrival_time).toLocaleTimeString("en-US", {
                  hour: "2-digit",
                  minute: "2-digit",
                }) : 'N/A'}
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
                  <span className="font-medium">{selectedFlight.flight_distance_km?.toLocaleString() || 'N/A'} km</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Airline:</span>
                  <span className="font-medium">{selectedFlight.airline.airline_name}</span>
                </div>
              </div>
            </div>

            {selectedFlight.shared_flight_info && (
              <div className="pt-2 border-t">
                <div className="text-xs font-semibold text-muted-foreground mb-1">SHARED FLIGHT</div>
                <div className="text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Partner:</span>
                    <span className="font-medium">{selectedFlight.shared_flight_info.secondary_airline?.airline_name || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Flight #:</span>
                    <span className="font-medium">{selectedFlight.shared_flight_info.secondary_flight_number}</span>
                  </div>
                </div>
              </div>
            )}

            {selectedFlight.connecting_flight && (
              <div className="pt-2 border-t">
                <div className="text-xs font-semibold text-muted-foreground mb-1">CONNECTING FLIGHT</div>
                <div className="text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Flight #:</span>
                    <span className="font-medium">{selectedFlight.connecting_flight.connecting_flight_number}</span>
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
