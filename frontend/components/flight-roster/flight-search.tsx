"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Search, Filter, X, Calendar, Plane, MapPin, Building2, Clock } from "lucide-react";

interface FlightSearchProps {
  onSearch: (filters: FlightFilters) => void;
  onClear: () => void;
}

export interface FlightFilters {
  flightNumber?: string;
  startDate?: string;
  endDate?: string;
  sourceAirport?: string;
  destinationAirport?: string;
  airlineId?: number;
}

// Quick date presets
const getDatePreset = (days: number) => {
  const date = new Date();
  date.setDate(date.getDate() + days);
  return date.toISOString().slice(0, 16);
};

const DATE_PRESETS = [
  { label: 'Today', value: getDatePreset(0) },
  { label: 'Tomorrow', value: getDatePreset(1) },
  { label: 'Next Week', value: getDatePreset(7) },
];

export function FlightSearch({ onSearch, onClear }: FlightSearchProps) {
  const [filters, setFilters] = useState<FlightFilters>({});
  const [airlines, setAirlines] = useState<Array<{ id: number; airline_name: string; airline_code: string }>>([]);
  const [airports, setAirports] = useState<Array<{ id: number; airport_code: string; airport_name: string }>>([]);
  const [showFilters, setShowFilters] = useState(false);

  // Fetch airlines and airports on mount
  useEffect(() => {
    fetchAirlines();
    fetchAirports();
  }, []);

  const fetchAirlines = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/flight-info/airlines`);
      if (response.ok) {
        const data = await response.json();
        setAirlines(data);
      }
    } catch (error) {
      console.error('Failed to fetch airlines:', error);
    }
  };

  const fetchAirports = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/flight-info/airports`);
      if (response.ok) {
        const data = await response.json();
        setAirports(data);
      }
    } catch (error) {
      console.error('Failed to fetch airports:', error);
    }
  };

  const handleSearch = () => {
    onSearch(filters);
  };

  const handleClear = () => {
    setFilters({});
    onClear();
  };

  const updateFilter = (key: keyof FlightFilters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const hasActiveFilters = Object.values(filters).some(v => v !== undefined && v !== '');

  const setDatePreset = (date: string) => {
    setFilters(prev => ({ ...prev, startDate: date }));
  };

  return (
    <Card className="border border-gray-200 shadow-sm">
      <CardHeader className="border-b bg-white">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-xl flex items-center gap-2 text-gray-900">
              <Search className="h-5 w-5 text-blue-600" />
              Flight Search
            </CardTitle>
            <CardDescription className="text-gray-600 mt-1">
              Search for flights by flight number or use filters
            </CardDescription>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center gap-2"
          >
            <Filter className="h-4 w-4" />
            {showFilters ? 'Hide' : 'Show'} Filters
          </Button>
        </div>
      </CardHeader>
      <CardContent className="pt-6 space-y-6">
        {/* Quick Search - Flight Number */}
        <div className="space-y-2">
          <Label htmlFor="flightNumber" className="text-sm font-medium text-gray-700">
            Flight Number
          </Label>
          <div className="flex gap-2">
            <Input
              id="flightNumber"
              placeholder="Enter flight number (e.g., AA2500, BA9001)"
              value={filters.flightNumber || ''}
              onChange={(e) => updateFilter('flightNumber', e.target.value.toUpperCase())}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              className="font-mono"
            />
            <Button onClick={handleSearch} className="px-6">
              <Search className="h-4 w-4 mr-2" />
              Search
            </Button>
          </div>
        </div>

        {/* Quick Date Selection */}
        <div className="space-y-2">
          <Label className="text-sm font-medium text-gray-700">Quick Date</Label>
          <div className="flex gap-2">
            {DATE_PRESETS.map((preset, idx) => (
              <Button
                key={idx}
                variant="outline"
                size="sm"
                onClick={() => {
                  setDatePreset(preset.value);
                  setShowFilters(true);
                }}
                className="flex-1"
              >
                <Clock className="h-4 w-4 mr-2" />
                {preset.label}
              </Button>
            ))}
          </div>
        </div>

        {/* Advanced Filters */}
        {showFilters && (
          <div className="space-y-4 pt-4 border-t">
            <h3 className="font-semibold text-gray-900">Advanced Filters</h3>

            {/* Date Range */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="startDate" className="text-sm font-medium text-gray-700">
                  Departure From
                </Label>
                <Input
                  id="startDate"
                  type="datetime-local"
                  value={filters.startDate || ''}
                  onChange={(e) => updateFilter('startDate', e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="endDate" className="text-sm font-medium text-gray-700">
                  Departure Until
                </Label>
                <Input
                  id="endDate"
                  type="datetime-local"
                  value={filters.endDate || ''}
                  onChange={(e) => updateFilter('endDate', e.target.value)}
                />
              </div>
            </div>

            {/* Airports */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="sourceAirport" className="text-sm font-medium text-gray-700">
                  From Airport
                </Label>
                <Select
                  value={filters.sourceAirport}
                  onValueChange={(value) => updateFilter('sourceAirport', value)}
                >
                  <SelectTrigger id="sourceAirport">
                    <SelectValue placeholder="Select departure airport" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">All Airports</SelectItem>
                    {airports.map((airport) => (
                      <SelectItem key={airport.id} value={airport.airport_code}>
                        {airport.airport_code} - {airport.airport_name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="destinationAirport" className="text-sm font-medium text-gray-700">
                  To Airport
                </Label>
                <Select
                  value={filters.destinationAirport}
                  onValueChange={(value) => updateFilter('destinationAirport', value)}
                >
                  <SelectTrigger id="destinationAirport">
                    <SelectValue placeholder="Select arrival airport" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">All Airports</SelectItem>
                    {airports.map((airport) => (
                      <SelectItem key={airport.id} value={airport.airport_code}>
                        {airport.airport_code} - {airport.airport_name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Airline */}
            <div className="space-y-2">
              <Label htmlFor="airline" className="text-sm font-medium text-gray-700">
                Airline
              </Label>
              <Select
                value={filters.airlineId?.toString()}
                onValueChange={(value) => updateFilter('airlineId', value ? parseInt(value) : undefined)}
              >
                <SelectTrigger id="airline">
                  <SelectValue placeholder="Select airline" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Airlines</SelectItem>
                  {airlines.map((airline) => (
                    <SelectItem key={airline.id} value={airline.id.toString()}>
                      {airline.airline_code} - {airline.airline_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2 pt-2">
              <Button onClick={handleSearch} className="flex-1">
                <Search className="h-4 w-4 mr-2" />
                Apply Filters
              </Button>
              {hasActiveFilters && (
                <Button onClick={handleClear} variant="outline" className="flex-1">
                  <X className="h-4 w-4 mr-2" />
                  Clear All
                </Button>
              )}
            </div>
          </div>
        )}

        {/* Active Filters Summary */}
        {hasActiveFilters && (
          <div className="pt-4 border-t bg-gray-50 p-3 rounded-lg">
            <p className="text-sm font-medium text-gray-700 mb-2">
              Active Filters:
            </p>
            <div className="flex flex-wrap gap-2">
              {filters.flightNumber && (
                <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-md text-sm flex items-center gap-1">
                  Flight: {filters.flightNumber}
                  <X
                    className="h-3 w-3 cursor-pointer hover:text-blue-600"
                    onClick={() => updateFilter('flightNumber', '')}
                  />
                </span>
              )}
              {filters.sourceAirport && (
                <span className="px-3 py-1 bg-green-100 text-green-800 rounded-md text-sm flex items-center gap-1">
                  From: {filters.sourceAirport}
                  <X
                    className="h-3 w-3 cursor-pointer hover:text-green-600"
                    onClick={() => updateFilter('sourceAirport', '')}
                  />
                </span>
              )}
              {filters.destinationAirport && (
                <span className="px-3 py-1 bg-red-100 text-red-800 rounded-md text-sm flex items-center gap-1">
                  To: {filters.destinationAirport}
                  <X
                    className="h-3 w-3 cursor-pointer hover:text-red-600"
                    onClick={() => updateFilter('destinationAirport', '')}
                  />
                </span>
              )}
              {filters.startDate && (
                <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-md text-sm flex items-center gap-1">
                  After: {new Date(filters.startDate).toLocaleDateString()}
                  <X
                    className="h-3 w-3 cursor-pointer hover:text-purple-600"
                    onClick={() => updateFilter('startDate', '')}
                  />
                </span>
              )}
              {filters.endDate && (
                <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-md text-sm flex items-center gap-1">
                  Before: {new Date(filters.endDate).toLocaleDateString()}
                  <X
                    className="h-3 w-3 cursor-pointer hover:text-purple-600"
                    onClick={() => updateFilter('endDate', '')}
                  />
                </span>
              )}
              {filters.airlineId && (
                <span className="px-3 py-1 bg-indigo-100 text-indigo-800 rounded-md text-sm flex items-center gap-1">
                  Airline: {airlines.find(a => a.id === filters.airlineId)?.airline_code}
                  <X
                    className="h-3 w-3 cursor-pointer hover:text-indigo-600"
                    onClick={() => updateFilter('airlineId', undefined)}
                  />
                </span>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
