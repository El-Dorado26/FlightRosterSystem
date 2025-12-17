"use client";

import { useState, useEffect } from "react";
import { FlightSelector } from "@/components/flight-roster/flight-selector";
import { TabularView } from "@/components/flight-roster/tabular-view";
import { PlaneView } from "@/components/flight-roster/plane-view";
import { ExtendedView } from "@/components/flight-roster/extended-view";
import { FlightStatistics } from "@/components/flight-roster/flight-statistics";
import { useAuth } from "@/contexts/AuthContext";
import { FeatureGuard } from "@/components/auth/role-guard";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { LayoutGrid, Table2, Plane, Download, Database, BarChart3, LogOut, Search, Loader2 } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const STORAGE_KEYS = {
  FLIGHTS: 'dashboard_flights',
  SELECTED_FLIGHT_ID: 'dashboard_selected_flight_id',
  SELECTED_FLIGHT_DATA: 'dashboard_selected_flight_data',
  ACTIVE_VIEW: 'dashboard_active_view',
};

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
  const [crewSelectionMode, setCrewSelectionMode] = useState<"auto" | "manual">("auto");
  const [seatAssignmentMode, setSeatAssignmentMode] = useState<"auto" | "manual">("auto");
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [flightCache, setFlightCache] = useState<Map<number, any>>(new Map());
  const [isFetching, setIsFetching] = useState(false);
  const [isInitialLoad, setIsInitialLoad] = useState(true);
  const [loadingFlightId, setLoadingFlightId] = useState<number | null>(null);
  const [isGeneratingRoster, setIsGeneratingRoster] = useState(false);
  const [exportOptions, setExportOptions] = useState({
    flightDetails: true,
    flightCrew: true,
    cabinCrew: true,
    passengers: true,
  });
  const { logout } = useAuth();

  useEffect(() => {
    const restoreState = () => {
      try {
        if (typeof window !== 'undefined') {
          const cachedFlights = sessionStorage.getItem(STORAGE_KEYS.FLIGHTS);
          if (cachedFlights) {
            const flightsData = JSON.parse(cachedFlights);
            setFlights(flightsData);
            setFilteredFlights(flightsData);
          }
          
          const cachedView = sessionStorage.getItem(STORAGE_KEYS.ACTIVE_VIEW);
          if (cachedView) {
            setActiveView(cachedView);
          }
          
          const cachedFlightId = sessionStorage.getItem(STORAGE_KEYS.SELECTED_FLIGHT_ID);
          const cachedFlightData = sessionStorage.getItem(STORAGE_KEYS.SELECTED_FLIGHT_DATA);
          
          if (cachedFlightData) {
            // Immediately restore the cached flight data to avoid empty state
            const flightData = JSON.parse(cachedFlightData);
            setSelectedFlight(flightData);
            
            // Also update the flight cache
            setFlightCache(prev => new Map(prev).set(flightData.id, flightData));
            
            // Fetch fresh data in background (optional - for up-to-date info)
            if (cachedFlightId) {
              const flightId = parseInt(cachedFlightId);
              fetchFlightDetails(flightId);
            }
          } else if (cachedFlightId && cachedFlights) {
            const flightId = parseInt(cachedFlightId);
            const flightsData = JSON.parse(cachedFlights);
            const flight = flightsData.find((f: any) => f.id === flightId);
            if (flight) {
              // Fetch full details for this flight
              fetchFlightDetails(flightId);
            }
          }
        }
      } catch (error) {
        console.error('Failed to restore dashboard state:', error);
      }
    };

    restoreState();
  }, []);

  // Fetch all flights on mount (only if not cached)
  useEffect(() => {
    if (isInitialLoad) {
      const cachedFlights = typeof window !== 'undefined' 
        ? sessionStorage.getItem(STORAGE_KEYS.FLIGHTS) 
        : null;
      
      if (!cachedFlights) {
        fetchFlights();
      } else {
        setLoading(false);
      }
      setIsInitialLoad(false);
    }
  }, [isInitialLoad]);

  const fetchFlights = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/flight-info/`);
      if (response.ok) {
        const data = await response.json();
        setFlights(data);
        setFilteredFlights(data);
        
        // Save to sessionStorage
        if (typeof window !== 'undefined') {
          sessionStorage.setItem(STORAGE_KEYS.FLIGHTS, JSON.stringify(data));
        }
        
        if (data.length > 0) {
          // Only fetch first flight if no flight is currently selected
          if (!selectedFlight) {
            await fetchFlightDetails(data[0].id);
          }
        }
      }
    } catch (error) {
      console.error('Failed to fetch flights:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchFlightDetails = async (flightId: number) => {
    // Prevent duplicate fetches
    if (isFetching) {
      console.log('Already fetching, skipping duplicate request');
      return;
    }
    
    // Check cache first
    if (flightCache.has(flightId)) {
      console.log(`Using cached data for flight ${flightId}`);
      setSelectedFlight(flightCache.get(flightId));
      setLoadingFlightId(null);
      return;
    }
    
    try {
      setIsFetching(true);
      setLoadingFlightId(flightId);
      
      // Single optimized request - backend returns all data including crew and passengers
      const flightResponse = await fetch(`${API_URL}/flight-info/${flightId}`);
      if (!flightResponse.ok) {
        throw new Error('Failed to fetch flight details');
      }
      
      const flightData = await flightResponse.json();
      
      // The backend now includes flight_crew, cabin_crew, and passengers in the response
      // Only make additional requests if data is missing (fallback)
      if (!flightData.flight_crew || flightData.flight_crew.length === 0) {
        const flightCrewResponse = await fetch(`${API_URL}/flight-crew/flights/${flightId}/crew`);
        if (flightCrewResponse.ok) {
          flightData.flight_crew = await flightCrewResponse.json();
        }
      }
      
      if (!flightData.cabin_crew || flightData.cabin_crew.length === 0) {
        const cabinCrewResponse = await fetch(`${API_URL}/cabin-crew/flight/${flightId}`);
        if (cabinCrewResponse.ok) {
          flightData.cabin_crew = await cabinCrewResponse.json();
        }
      }
        sessionStorage.setItem(STORAGE_KEYS.SELECTED_FLIGHT_DATA, JSON.stringify(flightData));
      
      if (!flightData.passengers || flightData.passengers.length === 0) {
        const passengersResponse = await fetch(`${API_URL}/passenger/?flight_id=${flightId}`);
        if (passengersResponse.ok) {
          flightData.passengers = await passengersResponse.json();
        }
      }

      // Cache the result
      setFlightCache(prev => new Map(prev).set(flightId, flightData));
      setSelectedFlight(flightData);
      
      // Save to sessionStorage
      if (typeof window !== 'undefined') {
        sessionStorage.setItem(STORAGE_KEYS.SELECTED_FLIGHT_ID, flightId.toString());
      }
    } catch (error) {
      console.error('Failed to fetch flight details:', error);
    } finally {
      setIsFetching(false);
      setLoadingFlightId(null);
    }
  };

  const handleFlightSelect = async (flight: any) => {
    // Immediately update UI to show selected flight (optimistic update)
    const basicFlightData = {
      ...flight,
      flight_crew: [],
      cabin_crew: [],
      passengers: []
    };
    setSelectedFlight(basicFlightData);
    
    await fetchFlightDetails(flight.id);
  };

  useEffect(() => {
    if (typeof window !== 'undefined' && activeView) {
      sessionStorage.setItem(STORAGE_KEYS.ACTIVE_VIEW, activeView);
    }
  }, [activeView]);



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
    
    alert(`✅ Export successful!\n\nFlight: ${selectedFlight.flight_number}\nSections: ${data.export_metadata.exported_sections.join(", ")}\n\nFile downloaded.`);
  };

  const handleGenerateRoster = async () => {
    if (!selectedFlight) return;

    setIsGeneratingRoster(true);
    try {
      const response = await fetch(`${API_URL}/roster/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          flight_id: selectedFlight.id,
          roster_name: `${selectedFlight.flight_number} - ${new Date().toLocaleDateString()}`,
          generated_by: "Dashboard User",
          database_type: databaseType,
          auto_select_crew: crewSelectionMode === "auto",
          auto_assign_seats: seatAssignmentMode === "auto"
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate roster');
      }

      const rosterData = await response.json();
      setGenerateRosterDialogOpen(false);
      
      // Show detailed success notification
      const metadata = rosterData.metadata || {};
      alert(`✅ Roster generated and saved to ${databaseType.toUpperCase()} database!\n\n` +
        `Roster ID: ${rosterData.id}\n` +
        `Flight: ${selectedFlight.flight_number}\n` +
        `Generated at: ${new Date(rosterData.generated_at).toLocaleString()}\n\n` +
        `Crew Selection: ${crewSelectionMode.toUpperCase()}\n` +
        `Flight Crew: ${metadata.total_flight_crew || 0}\n` +
        `Cabin Crew: ${metadata.total_cabin_crew || 0}\n\n` +
        `Seat Assignment: ${seatAssignmentMode.toUpperCase()}\n` +
        `Seats Assigned: ${metadata.seats_assigned || 0}/${metadata.total_passengers || 0}\n\n` +
        `You can view it in "View Saved Rosters"`
      );
      
      // Refresh flight details to show updated assignments
      await fetchFlightDetails(selectedFlight.id);
      
    } catch (error: any) {
      console.error('Failed to generate roster:', error);
      alert(`❌ Failed to generate roster.\n\n${error.message || 'Please try again.'}`);
    } finally {
      setIsGeneratingRoster(false);
    }
  };

  const fetchSavedRosters = async () => {
    try {
      console.log('Fetching saved rosters from:', `${API_URL}/roster/`);
      const response = await fetch(`${API_URL}/roster/`);
      if (response.ok) {
        const rosters = await response.json();
        console.log('Fetched rosters:', rosters);
        setSavedRosters(rosters);
      } else {
        console.error('Failed to fetch rosters, status:', response.status);
        setSavedRosters([]);
      }
    } catch (error) {
      console.error('Failed to fetch rosters:', error);
      setSavedRosters([]);
    }
  };

  const handleViewRoster = async (rosterId: string | number) => {
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
      } else {
        alert('Failed to load roster. Roster may not exist.');
      }
    } catch (error) {
      console.error('Failed to view roster:', error);
      alert('Failed to load roster. Please try again.');
    }
  };

  const handleExportRoster = async (rosterId: string | number) => {
    try {
      // Use export endpoint to get JSON data
      const response = await fetch(`${API_URL}/roster/${rosterId}`);
      if (response.ok) {
        const roster = await response.json();
        
        // Create export data
        const exportData = {
          roster_id: roster.id,
          roster_name: roster.roster_name,
          generated_at: roster.generated_at,
          generated_by: roster.generated_by,
          database_type: roster.database_type,
          flight_data: roster.roster_data,
          metadata: roster.metadata
        };
        
        // Download as JSON file
        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `roster_${roster.roster_name.replace(/\s+/g, '_')}_${rosterId}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        alert('✅ Roster exported successfully!');
      } else {
        alert('Failed to export roster. Roster may not exist.');
      }
    } catch (error) {
      console.error('Failed to export roster:', error);
      alert('Failed to export roster. Please try again.');
    }
  };

  const handleDeleteRoster = async (rosterId: string | number) => {
    if (!confirm('Are you sure you want to delete this roster?')) return;

    try {
      const response = await fetch(`${API_URL}/roster/${rosterId}`, {
        method: 'DELETE'
      });
      if (response.ok || response.status === 204) {
        alert('✅ Roster deleted successfully!');
        fetchSavedRosters();
      } else {
        alert('Failed to delete roster. Roster may not exist.');
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
        <div className="flex items-center justify-between bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="flex items-center gap-4">
            <div className="bg-blue-600 rounded-lg p-3">
              <Plane className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Flight Roster Management
              </h1>
              <p className="text-sm text-gray-500 mt-1 font-medium">
                Personnel & Passenger Operations System
              </p>
            </div>
          </div>
          {selectedFlight && (
            <div className="flex gap-2">
              <FeatureGuard feature="save">
                <Button 
                  onClick={() => setGenerateRosterDialogOpen(true)} 
                  className="flex items-center gap-2 bg-green-600 hover:bg-green-700"
                >
                  <LayoutGrid className="h-4 w-4" />
                  Generate Roster
                </Button>
              </FeatureGuard>
              <FeatureGuard feature="save">
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
              </FeatureGuard>
              <FeatureGuard feature="export">
                <Button onClick={() => setExportDialogOpen(true)} variant="outline" className="flex items-center gap-2">
                  <Download className="h-4 w-4" />
                  Export
                </Button>
              </FeatureGuard>
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
                    className={`flex items-center gap-3 p-4 border-2 rounded-lg transition-all ${
                      databaseType === "nosql"
                        ? "border-green-600 bg-green-50"
                        : "border-gray-200 hover:border-gray-300"
                    }`}
                  >
                    <Database className="h-8 w-8 text-green-600" />
                    <div className="text-left">
                      <div className="font-semibold">NoSQL</div>
                      <div className="text-xs text-gray-600">MongoDB database</div>
                    </div>
                  </button>
                </div>
              </div>

              <div className="space-y-3">
                <label className="text-sm font-medium">Crew Selection Method</label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    onClick={() => setCrewSelectionMode("auto")}
                    className={`flex items-center gap-3 p-4 border-2 rounded-lg transition-all ${
                      crewSelectionMode === "auto"
                        ? "border-green-600 bg-green-50"
                        : "border-gray-200 hover:border-gray-300"
                    }`}
                  >
                    <LayoutGrid className="h-8 w-8 text-green-600" />
                    <div className="text-left">
                      <div className="font-semibold">Automatic</div>
                      <div className="text-xs text-gray-600">AI selects qualified crew</div>
                    </div>
                  </button>
                  <button
                    onClick={() => setCrewSelectionMode("manual")}
                    disabled
                    className="flex items-center gap-3 p-4 border-2 rounded-lg opacity-50 cursor-not-allowed"
                  >
                    <LayoutGrid className="h-8 w-8 text-gray-400" />
                    <div className="text-left">
                      <div className="font-semibold">Manual</div>
                      <div className="text-xs text-gray-600">Coming soon</div>
                    </div>
                  </button>
                </div>
              </div>

              <div className="space-y-3">
                <label className="text-sm font-medium">Passenger Seat Assignment</label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    onClick={() => setSeatAssignmentMode("auto")}
                    className={`flex items-center gap-3 p-4 border-2 rounded-lg transition-all ${
                      seatAssignmentMode === "auto"
                        ? "border-green-600 bg-green-50"
                        : "border-gray-200 hover:border-gray-300"
                    }`}
                  >
                    <Plane className="h-8 w-8 text-green-600" />
                    <div className="text-left">
                      <div className="font-semibold">Automatic</div>
                      <div className="text-xs text-gray-600">Auto-assign empty seats</div>
                    </div>
                  </button>
                  <button
                    onClick={() => setSeatAssignmentMode("manual")}
                    className={`flex items-center gap-3 p-4 border-2 rounded-lg transition-all ${
                      seatAssignmentMode === "manual"
                        ? "border-blue-600 bg-blue-50"
                        : "border-gray-200 hover:border-gray-300"
                    }`}
                  >
                    <Plane className="h-8 w-8 text-blue-600" />
                    <div className="text-left">
                      <div className="font-semibold">Keep Current</div>
                      <div className="text-xs text-gray-600">Don't change seats</div>
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
              <Button variant="outline" onClick={() => setGenerateRosterDialogOpen(false)} disabled={isGeneratingRoster}>
                Cancel
              </Button>
              <Button onClick={handleGenerateRoster} className="bg-green-600 hover:bg-green-700" disabled={isGeneratingRoster}>
                {isGeneratingRoster ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Generating Roster...
                  </>
                ) : (
                  <>
                    <LayoutGrid className="h-4 w-4 mr-2" />
                    Generate & Save Roster
                  </>
                )}
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
                          <FeatureGuard feature="export">
                            <Button 
                              size="sm" 
                              variant="outline"
                              onClick={() => handleExportRoster(roster.id)}
                            >
                              <Download className="h-4 w-4" />
                            </Button>
                          </FeatureGuard>
                          <FeatureGuard feature="delete">
                            <Button 
                              size="sm" 
                              variant="destructive"
                              onClick={() => handleDeleteRoster(roster.id)}
                            >
                              Delete
                            </Button>
                          </FeatureGuard>
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

          {!loading && (
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              {/* Left Sidebar - Flight Selector */}
              <div className="lg:col-span-1">
                {filteredFlights.length > 0 ? (
                  <FlightSelector
                    flights={filteredFlights}
                    selectedFlight={selectedFlight}
                    onFlightSelect={handleFlightSelect}
                    isLoading={loadingFlightId !== null}
                  />
                ) : (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Search className="h-5 w-5" />
                        Available Flights
                      </CardTitle>
                      <CardDescription>No flights available</CardDescription>
                    </CardHeader>
                    <CardContent className="text-center py-8">
                      <Plane className="h-16 w-16 mx-auto text-gray-300 mb-4" />
                      <p className="text-sm text-gray-500">
                        No flights found in the database.
                        <br />
                        Please add flights to get started.
                      </p>
                    </CardContent>
                  </Card>
                )}
              </div>

              {/* Main Content Area */}
              <div className="lg:col-span-3">
                {selectedFlight ? (
                  <div className="relative">
                    {loadingFlightId !== null && (
                      <div className="absolute inset-0 bg-white/80 backdrop-blur-sm z-10 flex items-center justify-center rounded-lg">
                        <div className="text-center">
                          <Loader2 className="h-12 w-12 animate-spin text-blue-500 mx-auto mb-3" />
                          <p className="text-sm text-gray-600 font-medium">Loading flight data...</p>
                        </div>
                      </div>
                    )}
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
                  </div>
                ) : (
                  <Card className="border-none shadow-xl bg-white">
                    <CardContent className="relative pt-20 pb-20">
                      <div className="text-center max-w-5xl mx-auto">
                        
                        <div className="mb-6">
                          <h2 className="text-6xl font-light text-gray-800 mb-3 tracking-tight">
                            {filteredFlights.length === 0 
                              ? "No Flights Available" 
                              : "Flight Operations"}
                          </h2>
                          <div className="w-24 h-1 bg-gradient-to-r from-blue-500 to-blue-600 mx-auto rounded-full"></div>
                        </div>
                        
                        <p className="text-xl text-gray-500 mb-16 max-w-2xl mx-auto font-light leading-relaxed">
                          {filteredFlights.length === 0
                            ? "The database currently has no flights. Please add flights to the system to begin managing rosters."
                            : "Comprehensive crew management and passenger coordination"}
                        </p>
                        
                        {filteredFlights.length > 0 && (
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
                            <div className="group relative overflow-hidden bg-gradient-to-br from-blue-50 to-white rounded-2xl p-8 border border-gray-100 hover:border-blue-200 transition-all duration-500 hover:shadow-xl">
                              <div className="relative z-10">
                                <div className="w-14 h-14 bg-blue-500 rounded-xl flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300">
                                  <BarChart3 className="h-7 w-7 text-white" />
                                </div>
                                <h3 className="font-semibold text-gray-900 mb-2 text-lg">Live Analytics</h3>
                                <p className="text-sm text-gray-600 leading-relaxed">Real-time flight metrics and crew availability</p>
                              </div>
                              <div className="absolute top-0 right-0 w-32 h-32 bg-blue-100 rounded-full -mr-16 -mt-16 opacity-20"></div>
                            </div>
                            
                            <div className="group relative overflow-hidden bg-gradient-to-br from-purple-50 to-white rounded-2xl p-8 border border-gray-100 hover:border-purple-200 transition-all duration-500 hover:shadow-xl">
                              <div className="relative z-10">
                                <div className="w-14 h-14 bg-purple-500 rounded-xl flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300">
                                  <LayoutGrid className="h-7 w-7 text-white" />
                                </div>
                                <h3 className="font-semibold text-gray-900 mb-2 text-lg">Dynamic Views</h3>
                                <p className="text-sm text-gray-600 leading-relaxed">Flexible layouts for optimal workflow</p>
                              </div>
                              <div className="absolute top-0 right-0 w-32 h-32 bg-purple-100 rounded-full -mr-16 -mt-16 opacity-20"></div>
                            </div>
                            
                            <div className="group relative overflow-hidden bg-gradient-to-br from-green-50 to-white rounded-2xl p-8 border border-gray-100 hover:border-green-200 transition-all duration-500 hover:shadow-xl">
                              <div className="relative z-10">
                                <div className="w-14 h-14 bg-green-500 rounded-xl flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300">
                                  <Download className="h-7 w-7 text-white" />
                                </div>
                                <h3 className="font-semibold text-gray-900 mb-2 text-lg">Smart Export</h3>
                                <p className="text-sm text-gray-600 leading-relaxed">Detailed reports in multiple formats</p>
                              </div>
                              <div className="absolute top-0 right-0 w-32 h-32 bg-green-100 rounded-full -mr-16 -mt-16 opacity-20"></div>
                            </div>
                          </div>
                        )}
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
