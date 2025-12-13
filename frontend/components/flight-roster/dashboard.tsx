"use client";

import { useState, useEffect } from "react";
import { Flight } from "@/lib/mock-data";
import { FlightSearch, FlightFilters } from "@/components/flight-roster/flight-search";
import { FlightSelector } from "@/components/flight-roster/flight-selector";
import { TabularView } from "@/components/flight-roster/tabular-view";
import { PlaneView } from "@/components/flight-roster/plane-view";
import { ExtendedView } from "@/components/flight-roster/extended-view";
import { FlightStatistics } from "@/components/flight-roster/flight-statistics";
import { useAuth } from "@/contexts/AuthContext";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { LayoutGrid, Table2, Plane, Download, Database, BarChart3, LogOut, Search } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function FlightRosterDashboard() {
  const [flights, setFlights] = useState<any[]>([]);
  const [filteredFlights, setFilteredFlights] = useState<any[]>([]);
  const [selectedFlight, setSelectedFlight] = useState<any | null>(null);
  const [activeView, setActiveView] = useState<string>("statistics");
  const [exportDialogOpen, setExportDialogOpen] = useState(false);
  const [rostersDialogOpen, setRostersDialogOpen] = useState(false);
  const [generateRosterDialogOpen, setGenerateRosterDialogOpen] = useState(false);
  const [savedRosters, setSavedRosters] = useState<any[]>([]);
  const [databaseType, setDatabaseType] = useState<"sql" | "nosql">("sql");
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [exportOptions, setExportOptions] = useState({
    flightDetails: true,
    flightCrew: true,
    cabinCrew: true,
    passengers: true,
  });
  const { logout } = useAuth();

  // Fetch all flights on mount
  useEffect(() => {
    fetchFlights();
  }, []);

  const fetchFlights = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/flight-info/`);
      if (response.ok) {
        const data = await response.json();
        if (data.length > 0) {
          setFlights(data);
          setFilteredFlights(data);
          // Fetch detailed data for first flight
          await fetchFlightDetails(data[0].id);
        } else {
          // Use mock data if no flights from API
          const mockFlights = getMockFlights();
          setFlights(mockFlights);
          setFilteredFlights(mockFlights);
          setSelectedFlight(mockFlights[0]);
        }
      } else {
        // Use mock data if API fails
        const mockFlights = getMockFlights();
        setFlights(mockFlights);
        setFilteredFlights(mockFlights);
        setSelectedFlight(mockFlights[0]);
      }
    } catch (error) {
      console.error('Failed to fetch flights:', error);
      // Use mock data if fetch fails
      const mockFlights = getMockFlights();
      setFlights(mockFlights);
      setFilteredFlights(mockFlights);
      setSelectedFlight(mockFlights[0]);
    } finally {
      setLoading(false);
    }
  };

  const fetchFlightDetails = async (flightId: number) => {
    try {
      const flightResponse = await fetch(`${API_URL}/flight-info/${flightId}`);
      const flightData = await flightResponse.json();

      const flightCrewResponse = await fetch(`${API_URL}/flight-crew/flights/${flightId}/crew`);
      const flightCrewData = flightCrewResponse.ok ? await flightCrewResponse.json() : [];

      const cabinCrewResponse = await fetch(`${API_URL}/cabin-crew/flight/${flightId}`);
      const cabinCrewData = cabinCrewResponse.ok ? await cabinCrewResponse.json() : [];

      const passengersResponse = await fetch(`${API_URL}/passenger/?flight_id=${flightId}`);
      const passengersData = passengersResponse.ok ? await passengersResponse.json() : [];

      const completeFlightData = {
        ...flightData,
        flight_crew: flightCrewData,
        cabin_crew: cabinCrewData,
        passengers: passengersData
      };

      setSelectedFlight(completeFlightData);
    } catch (error) {
      console.error('Failed to fetch flight details:', error);
    }
  };

  const handleSearch = async (filters: FlightFilters) => {
    console.log('Search triggered with filters:', filters);
    
    // For flight number search, find and load the specific flight
    if (filters.flightNumber) {
      setLoading(true);
      
      try {
        const found = flights.find(f => f.flight_number === filters.flightNumber);
        if (found) {
          await fetchFlightDetails(found.id);
          setFilteredFlights([found]);
          setActiveView("tabular");
        }
      } catch (error) {
        console.error('Failed to load flight:', error);
      } finally {
        setLoading(false);
      }
      
      return;
    }

    // Original filter logic for other filters
    try {
      setLoading(true);
      
      let filtered = [...flights];

      if (filters.airlineId) {
        filtered = filtered.filter(f => f.airline_id === filters.airlineId);
      }

      if (filters.sourceAirport) {
        filtered = filtered.filter(f => {
          return f.departure_airport?.airport_code === filters.sourceAirport;
        });
      }

      if (filters.destinationAirport) {
        filtered = filtered.filter(f => {
          return f.arrival_airport?.airport_code === filters.destinationAirport;
        });
      }

      if (filters.startDate) {
        filtered = filtered.filter(f => new Date(f.departure_time) >= new Date(filters.startDate!));
      }

      if (filters.endDate) {
        filtered = filtered.filter(f => new Date(f.departure_time) <= new Date(filters.endDate!));
      }

      setFilteredFlights(filtered);
      if (filtered.length > 0) {
        await fetchFlightDetails(filtered[0].id);
        setActiveView("tabular");
      } else {
        setSelectedFlight(null);
      }
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const getMockFlights = () => {
    return [
      {
        id: 1,
        flight_number: "AA100",
        airline_id: "AA",
        airline: { name: "American Airlines", code: "AA" },
        departure_airport: { airport_code: "JFK", name: "John F. Kennedy International" },
        arrival_airport: { airport_code: "LAX", name: "Los Angeles International" },
        departure_time: new Date().toISOString(),
        arrival_time: new Date(Date.now() + 6 * 60 * 60 * 1000).toISOString(),
        status: "scheduled",
        vehicle_type: {
          type_code: "B738",
          total_seats: 189,
          seating_plan: { business: 16, economy: 150, rows: 32, seats_per_row: 6 }
        },
        flight_crew: [
          { id: 1, name: "John Smith", role: "Captain", age: 45, gender: "M", nationality: "USA", employee_id: "FC001", license_number: "ATL12345", seniority_level: "Senior", max_allowed_distance_km: 15000, hours_flown: 8500, seat_number: "Cockpit-1" },
          { id: 2, name: "Jane Doe", role: "First Officer", age: 38, gender: "F", nationality: "USA", employee_id: "FC002", license_number: "ATL12346", seniority_level: "Mid", max_allowed_distance_km: 12000, hours_flown: 5200, seat_number: "Cockpit-2" }
        ],
        cabin_crew: [
          { id: 1, name: "Sarah Johnson", attendant_type: "Purser", age: 35, gender: "F", nationality: "USA", employee_id: "CC001", seat_number: "Crew-1" },
          { id: 2, name: "Mike Wilson", attendant_type: "Flight Attendant", age: 28, gender: "M", nationality: "USA", employee_id: "CC002", seat_number: "Crew-2" },
          { id: 3, name: "Emily Brown", attendant_type: "Flight Attendant", age: 26, gender: "F", nationality: "USA", employee_id: "CC003", seat_number: "Crew-3" }
        ],
        passengers: [
          { id: 1, name: "Alice Anderson", seat_number: "1A", seat_type: "Business", age: 42, gender: "F", nationality: "USA", passport_number: "P123456" },
          { id: 2, name: "Bob Baker", seat_number: "1B", seat_type: "Business", age: 39, gender: "M", nationality: "UK", passport_number: "P123457" },
          { id: 3, name: "Charlie Chen", seat_number: "12A", seat_type: "Economy", age: 28, gender: "M", nationality: "China", passport_number: "P123458" },
          { id: 4, name: "Diana Davis", seat_number: "12B", seat_type: "Economy", age: 31, gender: "F", nationality: "Canada", passport_number: "P123459" },
          { id: 5, name: "Ethan Evans", seat_number: "12C", seat_type: "Economy", age: 45, gender: "M", nationality: "Australia", passport_number: "P123460" }
        ]
      },
      {
        id: 2,
        flight_number: "DL200",
        airline_id: "DL",
        airline: { name: "Delta Airlines", code: "DL" },
        departure_airport: { airport_code: "ATL", name: "Atlanta International" },
        arrival_airport: { airport_code: "LHR", name: "London Heathrow" },
        departure_time: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(),
        arrival_time: new Date(Date.now() + 10 * 60 * 60 * 1000).toISOString(),
        status: "scheduled",
        vehicle_type: {
          type_code: "A350",
          total_seats: 280,
          seating_plan: { business: 32, economy: 248, rows: 45, seats_per_row: 9 }
        },
        flight_crew: [
          { id: 3, name: "Robert Wilson", role: "Captain", age: 52, gender: "M", nationality: "USA", employee_id: "FC003", license_number: "ATL12347", seniority_level: "Senior", max_allowed_distance_km: 18000, hours_flown: 12000, seat_number: "Cockpit-1" }
        ],
        cabin_crew: [
          { id: 4, name: "Lisa Martinez", attendant_type: "Chief", age: 40, gender: "F", nationality: "USA", employee_id: "CC004", seat_number: "Crew-1" }
        ],
        passengers: []
      }
    ];
  };

  const handleQuickSearch = () => {
    console.log('Quick search clicked');
    console.log('Flights available:', flights.length);
    
    const flightToShow = flights.length > 0 ? flights[0] : getMockFlights()[0];
    
    setSelectedFlight(flightToShow);
    setFilteredFlights([flightToShow]);
    setActiveView("tabular");
  };

  const handleClearSearch = () => {
    setFilteredFlights(flights);
    if (flights.length > 0) {
      setSelectedFlight(flights[0]);
    }
  };

  const handleExportJSON = () => {
    if (!selectedFlight) return;

    const data: any = {
      export_metadata: {
        timestamp: new Date().toISOString(),
        flight_number: selectedFlight.flight_number,
        airline: selectedFlight.airline.airline_name,
        route: `${selectedFlight.departure_airport.airport_code} → ${selectedFlight.arrival_airport.airport_code}`,
        exported_sections: []
      }
    };

    if (exportOptions.flightDetails) {
      // Export flight details without nested crew/passengers
      const { flight_crew, cabin_crew, passengers, ...flightDetails } = selectedFlight;
      data.flight = flightDetails;
      data.export_metadata.exported_sections.push("Flight Details");
    }

    if (exportOptions.flightCrew) {
      data.flightCrew = selectedFlight.flight_crew;
      data.export_metadata.exported_sections.push("Flight Crew");
    }

    if (exportOptions.cabinCrew) {
      data.cabinCrew = selectedFlight.cabin_crew;
      data.export_metadata.exported_sections.push("Cabin Crew");
    }

    if (exportOptions.passengers) {
      data.passengers = selectedFlight.passengers;
      data.export_metadata.exported_sections.push("Passengers");
    }

    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `flight-roster-${selectedFlight.flight_number}-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    console.log("[MOCK] Exported flight data:", data);
    setExportDialogOpen(false);
    
    // Show success notification
    alert(`✅ Export successful!\n\nFlight: ${selectedFlight.flight_number}\nSections: ${data.export_metadata.exported_sections.join(", ")}\n\nFile downloaded.`);
  };

  const handleGenerateRoster = async () => {
    if (!selectedFlight) return;

    try {
      // Generate roster via API
      const response = await fetch(`${API_URL}/roster/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          flight_id: selectedFlight.id,
          roster_name: `${selectedFlight.flight_number} - ${new Date().toLocaleDateString()}`,
          generated_by: "Dashboard User",
          database_type: databaseType
        })
      });

      if (!response.ok) {
        throw new Error('Failed to generate roster');
      }

      const rosterData = await response.json();
      setGenerateRosterDialogOpen(false);
      
      // Show success notification
      alert(`✅ Roster generated and saved to ${databaseType.toUpperCase()} database!\n\nRoster ID: ${rosterData.id}\nFlight: ${selectedFlight.flight_number}\nGenerated at: ${new Date(rosterData.generated_at).toLocaleString()}\n\nYou can view it in "View Saved Rosters"`);
      
    } catch (error) {
      console.error('Failed to generate roster:', error);
      alert(`❌ Failed to generate roster. Please try again.`);
    }
  };

  const fetchSavedRosters = async () => {
    try {
      const response = await fetch(`${API_URL}/roster/`);
      if (response.ok) {
        const rosters = await response.json();
        setSavedRosters(rosters);
      }
    } catch (error) {
      console.error('Failed to fetch rosters:', error);
    }
  };

  const handleViewRoster = async (rosterId: number) => {
    try {
      const response = await fetch(`${API_URL}/roster/${rosterId}`);
      if (response.ok) {
        const roster = await response.json();
        // Create a flight object from roster data
        const flightFromRoster = {
          ...roster.roster_data.flight_info,
          flight_crew: roster.roster_data.flight_crew || [],
          cabin_crew: roster.roster_data.cabin_crew || [],
          passengers: roster.roster_data.passengers || [],
          airline: roster.roster_data.flight_info.airline,
          departure_airport: roster.roster_data.flight_info.route.departure,
          arrival_airport: roster.roster_data.flight_info.route.arrival,
          vehicle_type: roster.roster_data.flight_info.aircraft,
          departure_time: roster.roster_data.flight_info.schedule.departure_time,
          arrival_time: roster.roster_data.flight_info.schedule.arrival_time,
          date: roster.roster_data.flight_info.schedule.date,
        };
        setSelectedFlight(flightFromRoster);
        setRostersDialogOpen(false);
        setActiveView("tabular");
      }
    } catch (error) {
      console.error('Failed to view roster:', error);
      alert('Failed to load roster. Please try again.');
    }
  };

  const handleExportRoster = async (rosterId: number) => {
    try {
      const response = await fetch(`${API_URL}/roster/${rosterId}/download/json`);
      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `roster_${rosterId}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Failed to export roster:', error);
      alert('Failed to export roster. Please try again.');
    }
  };

  const handleDeleteRoster = async (rosterId: number) => {
    if (!confirm('Are you sure you want to delete this roster?')) return;

    try {
      const response = await fetch(`${API_URL}/roster/${rosterId}`, {
        method: 'DELETE'
      });
      if (response.ok) {
        alert('Roster deleted successfully!');
        fetchSavedRosters(); // Refresh the list
      }
    } catch (error) {
      console.error('Failed to delete roster:', error);
      alert('Failed to delete roster. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container mx-auto p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-gray-900">OpenAIrlines Roster Dashboard</h1>
            <p className="text-gray-600 mt-2">
              Flight Personnel & Passenger Management System
            </p>
          </div>
          {selectedFlight && (
            <div className="flex gap-2">
              <Button 
                onClick={() => setGenerateRosterDialogOpen(true)} 
                className="flex items-center gap-2 bg-green-600 hover:bg-green-700"
              >
                <LayoutGrid className="h-4 w-4" />
                Generate Roster
              </Button>
              <Button 
                onClick={() => {
                  fetchSavedRosters();
                  setRostersDialogOpen(true);
                }} 
                variant="outline" 
                className="flex items-center gap-2"
              >
                <Database className="h-4 w-4" />
                View Saved Rosters
              </Button>
              <Button onClick={() => setExportDialogOpen(true)} variant="outline" className="flex items-center gap-2">
                <Download className="h-4 w-4" />
                Export
              </Button>
              <Button onClick={logout} variant="destructive" className="flex items-center gap-2">
                <LogOut className="h-4 w-4" />
                Logout
              </Button>
            </div>
          )}
        </div>

        {/* Generate Roster Dialog */}
        <Dialog open={generateRosterDialogOpen} onOpenChange={setGenerateRosterDialogOpen}>
          <DialogContent onClose={() => setGenerateRosterDialogOpen(false)}>
            <DialogHeader>
              <DialogTitle>Generate Flight Roster</DialogTitle>
              <DialogDescription>
                Generate a complete roster snapshot for {selectedFlight?.flight_number}
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-4 py-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-semibold text-blue-900 mb-2">What will be included:</h3>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>✓ Complete flight information (route, schedule, aircraft)</li>
                  <li>✓ All flight crew members (pilots, engineers)</li>
                  <li>✓ All cabin crew members (attendants, chefs)</li>
                  <li>✓ All passenger details</li>
                  <li>✓ Occupancy and crew statistics</li>
                </ul>
              </div>

              <div className="space-y-3">
                <label className="text-sm font-medium">Select Database Type</label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    onClick={() => setDatabaseType("sql")}
                    className={`flex items-center gap-3 p-4 border-2 rounded-lg transition-all ${
                      databaseType === "sql"
                        ? "border-blue-600 bg-blue-50"
                        : "border-gray-200 hover:border-gray-300"
                    }`}
                  >
                    <Database className="h-8 w-8 text-blue-600" />
                    <div className="text-left">
                      <div className="font-semibold">SQL</div>
                      <div className="text-xs text-gray-600">PostgreSQL database</div>
                    </div>
                  </button>
                  <button
                    onClick={() => setDatabaseType("nosql")}
                    disabled
                    className="flex items-center gap-3 p-4 border-2 rounded-lg opacity-50 cursor-not-allowed"
                  >
                    <Database className="h-8 w-8 text-gray-400" />
                    <div className="text-left">
                      <div className="font-semibold">NoSQL</div>
                      <div className="text-xs text-gray-600">Not available yet</div>
                    </div>
                  </button>
                </div>
              </div>

              {selectedFlight && (
                <div className="bg-gray-50 rounded-lg p-4 text-sm">
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <span className="text-gray-600">Flight:</span>
                      <span className="ml-2 font-semibold">{selectedFlight.flight_number}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Aircraft:</span>
                      <span className="ml-2 font-semibold">{selectedFlight.vehicle_type?.aircraft_code}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Flight Crew:</span>
                      <span className="ml-2 font-semibold">{selectedFlight.flight_crew?.length || 0}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Cabin Crew:</span>
                      <span className="ml-2 font-semibold">{selectedFlight.cabin_crew?.length || 0}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Passengers:</span>
                      <span className="ml-2 font-semibold">{selectedFlight.passengers?.length || 0}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Capacity:</span>
                      <span className="ml-2 font-semibold">{selectedFlight.vehicle_type?.total_seats}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => setGenerateRosterDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleGenerateRoster} className="bg-green-600 hover:bg-green-700">
                <LayoutGrid className="h-4 w-4 mr-2" />
                Generate & Save Roster
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Export Dialog */}
        <Dialog open={exportDialogOpen} onOpenChange={setExportDialogOpen}>
          <DialogContent onClose={() => setExportDialogOpen(false)}>
            <DialogHeader>
              <DialogTitle>Export Flight Roster</DialogTitle>
              <DialogDescription>
                Select what data to include in the JSON export for {selectedFlight?.flight_number}
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-4 py-4">
              <div className="space-y-3">
                <label className="text-sm font-medium">Data to Export</label>
                <div className="space-y-2">
                  <label className="flex items-center gap-3 p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={exportOptions.flightDetails}
                      onChange={(e) =>
                        setExportOptions({ ...exportOptions, flightDetails: e.target.checked })
                      }
                      className="h-4 w-4 text-blue-600 rounded"
                    />
                    <div className="flex-1">
                      <div className="font-medium">Flight Details</div>
                      <div className="text-xs text-gray-600">
                        Basic flight information, route, and aircraft details
                      </div>
                    </div>
                  </label>

                  <label className="flex items-center gap-3 p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={exportOptions.flightCrew}
                      onChange={(e) =>
                        setExportOptions({ ...exportOptions, flightCrew: e.target.checked })
                      }
                      className="h-4 w-4 text-blue-600 rounded"
                    />
                    <div className="flex-1">
                      <div className="font-medium">Flight Crew</div>
                      <div className="text-xs text-gray-600">
                        Pilots and technical crew members
                      </div>
                    </div>
                  </label>

                  <label className="flex items-center gap-3 p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={exportOptions.cabinCrew}
                      onChange={(e) =>
                        setExportOptions({ ...exportOptions, cabinCrew: e.target.checked })
                      }
                      className="h-4 w-4 text-blue-600 rounded"
                    />
                    <div className="flex-1">
                      <div className="font-medium">Cabin Crew</div>
                      <div className="text-xs text-gray-600">
                        Flight attendants and cabin service staff
                      </div>
                    </div>
                  </label>

                  <label className="flex items-center gap-3 p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={exportOptions.passengers}
                      onChange={(e) =>
                        setExportOptions({ ...exportOptions, passengers: e.target.checked })
                      }
                      className="h-4 w-4 text-blue-600 rounded"
                    />
                    <div className="flex-1">
                      <div className="font-medium">Passengers</div>
                      <div className="text-xs text-gray-600">
                        Passenger list with seat assignments and details
                      </div>
                    </div>
                  </label>
                </div>
              </div>
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => setExportDialogOpen(false)}>
                Cancel
              </Button>
              <Button 
                onClick={handleExportJSON}
                disabled={!Object.values(exportOptions).some(v => v)}
              >
                <Download className="h-4 w-4 mr-2" />
                Export JSON
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Saved Rosters Dialog */}
        <Dialog open={rostersDialogOpen} onOpenChange={setRostersDialogOpen}>
          <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto" onClose={() => setRostersDialogOpen(false)}>
            <DialogHeader>
              <DialogTitle>Saved Rosters</DialogTitle>
              <DialogDescription>
                View, retrieve, and export previously saved rosters from the database
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-4 py-4">
              {savedRosters.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  No saved rosters found. Generate and save a roster first.
                </div>
              ) : (
                <div className="space-y-3">
                  {savedRosters.map((roster) => (
                    <div key={roster.id} className="border rounded-lg p-4 hover:bg-gray-50">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="font-semibold text-lg">{roster.roster_name}</h3>
                          <div className="text-sm text-gray-600 mt-1 space-y-1">
                            <p>Roster ID: #{roster.id}</p>
                            <p>Generated: {new Date(roster.generated_at).toLocaleString()}</p>
                            <p>Database: {roster.database_type.toUpperCase()}</p>
                            {roster.generated_by && <p>By: {roster.generated_by}</p>}
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => handleViewRoster(roster.id)}
                          >
                            View
                          </Button>
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => handleExportRoster(roster.id)}
                          >
                            <Download className="h-4 w-4" />
                          </Button>
                          <Button 
                            size="sm" 
                            variant="destructive"
                            onClick={() => handleDeleteRoster(roster.id)}
                          >
                            Delete
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => setRostersDialogOpen(false)}>
                Close
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Main Layout */}
        <div className="space-y-6">
          {loading && (
            <Card>
              <CardContent className="py-12 text-center">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent mb-4"></div>
                <p className="text-gray-600">Loading flights...</p>
              </CardContent>
            </Card>
          )}

          {!loading && filteredFlights.length === 0 && (
            <Card>
              <CardContent className="py-12 text-center">
                <p className="text-gray-600 text-lg">No flights found</p>
              </CardContent>
            </Card>
          )}

          {!loading && filteredFlights.length > 0 && (
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              {/* Left Sidebar - Flight Selector */}
              <div className="lg:col-span-1">
                <FlightSelector
                  flights={filteredFlights}
                  selectedFlight={selectedFlight}
                  onFlightSelect={setSelectedFlight}
                />
              </div>

              {/* Main Content Area */}
              <div className="lg:col-span-3">
                {selectedFlight ? (
                  <Tabs value={activeView} onValueChange={setActiveView} className="w-full">
                    <TabsList className="grid w-full grid-cols-4">
                      <TabsTrigger value="statistics" className="flex items-center gap-2">
                        <BarChart3 className="h-4 w-4" />
                        Statistics
                      </TabsTrigger>
                      <TabsTrigger value="tabular" className="flex items-center gap-2">
                        <Table2 className="h-4 w-4" />
                        Tabular View
                      </TabsTrigger>
                      <TabsTrigger value="plane" className="flex items-center gap-2">
                        <Plane className="h-4 w-4" />
                        Plane View
                      </TabsTrigger>
                      <TabsTrigger value="extended" className="flex items-center gap-2">
                        <LayoutGrid className="h-4 w-4" />
                        Extended View
                      </TabsTrigger>
                    </TabsList>

                    <TabsContent value="statistics" className="mt-6">
                      <FlightStatistics flight={selectedFlight} />
                    </TabsContent>

                    <TabsContent value="tabular" className="mt-6">
                      <TabularView flight={selectedFlight} />
                    </TabsContent>

                    <TabsContent value="plane" className="mt-6">
                      <PlaneView flight={selectedFlight} />
                    </TabsContent>

                    <TabsContent value="extended" className="mt-6">
                      <ExtendedView flight={selectedFlight} />
                    </TabsContent>
                  </Tabs>
                ) : (
                  <Card className="border-none shadow-lg bg-gradient-to-br from-blue-50 to-purple-50">
                    <CardContent className="pt-20 pb-20">
                      <div className="text-center max-w-2xl mx-auto">
                        <div className="relative inline-block mb-8">
                          <div className="absolute inset-0 bg-blue-200 rounded-full blur-3xl opacity-30 animate-pulse"></div>
                          <Plane className="h-32 w-32 mx-auto text-blue-500 relative animate-bounce" style={{ animationDuration: '3s' }} />
                        </div>
                        
                        <h2 className="text-3xl font-bold text-gray-900 mb-4">
                          Welcome to Flight Roster System
                        </h2>
                        
                        <p className="text-lg text-gray-600 mb-8 leading-relaxed">
                          Select a flight from the sidebar to explore comprehensive roster information, 
                          seat assignments, crew details, and passenger manifests.
                        </p>
                        
                        <div className="flex items-center justify-center gap-6 text-sm text-gray-500">
                          <div className="flex items-center gap-2">
                            <div className="h-2 w-2 bg-blue-500 rounded-full"></div>
                            <span>Real-time Data</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <div className="h-2 w-2 bg-purple-500 rounded-full"></div>
                            <span>Multiple Views</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <div className="h-2 w-2 bg-green-500 rounded-full"></div>
                            <span>Export Ready</span>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
