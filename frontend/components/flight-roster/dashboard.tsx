"use client";

import { useState } from "react";
import { mockFlights, Flight } from "@/lib/mock-data";
import { FlightSelector } from "@/components/flight-roster/flight-selector";
import { TabularView } from "@/components/flight-roster/tabular-view";
import { PlaneView } from "@/components/flight-roster/plane-view";
import { ExtendedView } from "@/components/flight-roster/extended-view";
import { FlightStatistics } from "@/components/flight-roster/flight-statistics";
import { FeatureGuard } from "@/components/auth/role-guard";
import { useAuth } from "@/lib/auth-context";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { LayoutGrid, Table2, Plane, Download, Database, BarChart3, LogOut } from "lucide-react";

export default function FlightRosterDashboard() {
  const [selectedFlight, setSelectedFlight] = useState<Flight | null>(mockFlights[0]);
  const [activeView, setActiveView] = useState<string>("statistics");
  const [exportDialogOpen, setExportDialogOpen] = useState(false);
  const [saveDialogOpen, setSaveDialogOpen] = useState(false);
  const [databaseType, setDatabaseType] = useState<"sql" | "nosql">("sql");
  const [exportOptions, setExportOptions] = useState({
    flightDetails: true,
    flightCrew: true,
    cabinCrew: true,
    passengers: true,
  });
  const { logout } = useAuth();

  const handleExportJSON = () => {
    if (!selectedFlight) return;

    const data: any = {};

    if (exportOptions.flightDetails) {
      // Export flight details without nested crew/passengers
      const { flight_crew, cabin_crew, passengers, ...flightDetails } = selectedFlight;
      data.flight = flightDetails;
    }

    if (exportOptions.flightCrew) {
      data.flightCrew = selectedFlight.flight_crew;
    }

    if (exportOptions.cabinCrew) {
      data.cabinCrew = selectedFlight.cabin_crew;
    }

    if (exportOptions.passengers) {
      data.passengers = selectedFlight.passengers;
    }

    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `flight-roster-${selectedFlight.flight_number}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    setExportDialogOpen(false);
  };

  const handleSaveToDatabase = (dbType: "sql" | "nosql") => {
    // Mock function - would integrate with backend
    alert(`Mock: Would save roster to ${dbType.toUpperCase()} database`);
    setSaveDialogOpen(false);
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
              <FeatureGuard feature="export">
                <Button onClick={() => setExportDialogOpen(true)} variant="outline" className="flex items-center gap-2">
                  <Download className="h-4 w-4" />
                  Export
                </Button>
              </FeatureGuard>
              <FeatureGuard feature="save">
                <Button onClick={() => setSaveDialogOpen(true)} className="flex items-center gap-2">
                  <Database className="h-4 w-4" />
                  Save to Database
                </Button>
              </FeatureGuard>
              <Button onClick={logout} variant="destructive" className="flex items-center gap-2">
                <LogOut className="h-4 w-4" />
                Logout
              </Button>
            </div>
          )}
        </div>

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

        {/* Save to Database Dialog */}
        <Dialog open={saveDialogOpen} onOpenChange={setSaveDialogOpen}>
          <DialogContent onClose={() => setSaveDialogOpen(false)}>
            <DialogHeader>
              <DialogTitle>Save to Database</DialogTitle>
              <DialogDescription>
                Select the database type to save the flight roster for {selectedFlight?.flight_number}
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-4 py-4">
              <div className="space-y-3">
                <label className="text-sm font-medium">Database Type</label>
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
                      <div className="text-xs text-gray-600">Relational database</div>
                    </div>
                  </button>
                  <button
                    onClick={() => setDatabaseType("nosql")}
                    className={`flex items-center gap-3 p-4 border-2 rounded-lg transition-all ${
                      databaseType === "nosql"
                        ? "border-blue-600 bg-blue-50"
                        : "border-gray-200 hover:border-gray-300"
                    }`}
                  >
                    <Database className="h-8 w-8 text-green-600" />
                    <div className="text-left">
                      <div className="font-semibold">NoSQL</div>
                      <div className="text-xs text-gray-600">Document database</div>
                    </div>
                  </button>
                </div>
              </div>
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => setSaveDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={() => handleSaveToDatabase(databaseType)}>
                <Database className="h-4 w-4 mr-2" />
                Save to {databaseType.toUpperCase()}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Main Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Left Sidebar - Flight Selector */}
          <div className="lg:col-span-1">
            <FlightSelector
              flights={mockFlights}
              selectedFlight={selectedFlight}
              onFlightSelect={setSelectedFlight}
            />

            {selectedFlight && (
              <Card className="mt-4">
                <CardHeader>
                  <CardTitle className="text-sm">Quick Stats</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Total Capacity:</span>
                    <span className="font-semibold">{selectedFlight.vehicle_type.total_seats}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Passengers:</span>
                    <span className="font-semibold">{selectedFlight.passengers.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Flight Crew:</span>
                    <span className="font-semibold">{selectedFlight.flight_crew.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Cabin Crew:</span>
                    <span className="font-semibold">{selectedFlight.cabin_crew.length}</span>
                  </div>
                  <div className="flex justify-between pt-2 border-t">
                    <span className="text-muted-foreground">Occupancy:</span>
                    <span className="font-semibold">
                      {Math.round(
                        (selectedFlight.passengers.length / selectedFlight.vehicle_type.total_seats) * 100
                      )}
                      %
                    </span>
                  </div>
                </CardContent>
              </Card>
            )}
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
              <Card>
                <CardHeader>
                  <CardTitle>Welcome to Flight Roster System</CardTitle>
                  <CardDescription>Please select a flight from the sidebar to begin</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-12">
                    <Plane className="h-24 w-24 mx-auto text-gray-300 mb-4" />
                    <p className="text-gray-500">
                      Select a flight to view roster information, seat assignments, and personnel details.
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
