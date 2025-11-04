"use client";

import { Flight } from "@/lib/mock-data";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Users, PlaneTakeoff, UserCheck } from "lucide-react";

interface ExtendedViewProps {
  flight: Flight;
}

export function ExtendedView({ flight }: ExtendedViewProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Extended View - Detailed Personnel Information</CardTitle>
        <CardDescription>
          Separate tables for each type of personnel on Flight {flight.flight_number}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="flight-crew" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="flight-crew" className="flex items-center gap-2">
              <PlaneTakeoff className="h-4 w-4" />
              Flight Crew ({flight.flight_crew.length})
            </TabsTrigger>
            <TabsTrigger value="cabin-crew" className="flex items-center gap-2">
              <UserCheck className="h-4 w-4" />
              Cabin Crew ({flight.cabin_crew.length})
            </TabsTrigger>
            <TabsTrigger value="passengers" className="flex items-center gap-2">
              <Users className="h-4 w-4" />
              Passengers ({flight.passengers.length})
            </TabsTrigger>
          </TabsList>

          {/* Flight Crew Tab */}
          <TabsContent value="flight-crew" className="space-y-4">
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Employee ID</TableHead>
                    <TableHead>Role</TableHead>
                    <TableHead>License</TableHead>
                    <TableHead>Seniority</TableHead>
                    <TableHead>Age</TableHead>
                    <TableHead>Gender</TableHead>
                    <TableHead>Nationality</TableHead>
                    <TableHead>Languages</TableHead>
                    <TableHead>Hours Flown</TableHead>
                    <TableHead>Max Distance (km)</TableHead>
                    <TableHead>Seat</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {flight.flight_crew.map((crew) => (
                    <TableRow key={crew.id}>
                      <TableCell className="font-medium">{crew.name}</TableCell>
                      <TableCell className="font-mono text-xs">{crew.employee_id}</TableCell>
                      <TableCell>
                        <Badge variant={crew.role === "Captain" ? "default" : "secondary"}>
                          {crew.role}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-mono text-xs">{crew.license_number}</TableCell>
                      <TableCell>
                        <Badge
                          variant={
                            crew.seniority_level === "Senior"
                              ? "default"
                              : crew.seniority_level === "Junior"
                              ? "secondary"
                              : "outline"
                          }
                        >
                          {crew.seniority_level}
                        </Badge>
                      </TableCell>
                      <TableCell>{crew.age}</TableCell>
                      <TableCell>{crew.gender}</TableCell>
                      <TableCell>{crew.nationality}</TableCell>
                      <TableCell className="text-xs">{crew.languages.join(", ")}</TableCell>
                      <TableCell>{crew.hours_flown.toLocaleString()}</TableCell>
                      <TableCell>{crew.max_allowed_distance_km.toLocaleString()}</TableCell>
                      <TableCell className="font-mono text-xs">{crew.seat_number}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="font-semibold text-blue-900 mb-2">Flight Crew Requirements</h4>
              <div className="text-sm text-blue-800 space-y-1">
                <div>✓ At least one Senior and one Junior pilot required</div>
                <div>✓ Maximum two trainees allowed per flight</div>
                <div>✓ All crew must be qualified for {flight.vehicle_type.aircraft_name}</div>
              </div>
            </div>
          </TabsContent>

          {/* Cabin Crew Tab */}
          <TabsContent value="cabin-crew" className="space-y-4">
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Employee ID</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Age</TableHead>
                    <TableHead>Gender</TableHead>
                    <TableHead>Nationality</TableHead>
                    <TableHead>Languages</TableHead>
                    <TableHead>Special Skills</TableHead>
                    <TableHead>Seat</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {flight.cabin_crew.map((crew) => (
                    <TableRow key={crew.id}>
                      <TableCell className="font-medium">{crew.name}</TableCell>
                      <TableCell className="font-mono text-xs">{crew.employee_id}</TableCell>
                      <TableCell>
                        <Badge
                          variant={
                            crew.attendant_type === "Chief"
                              ? "default"
                              : crew.attendant_type === "Chef"
                              ? "secondary"
                              : "outline"
                          }
                        >
                          {crew.attendant_type}
                        </Badge>
                      </TableCell>
                      <TableCell>{crew.age}</TableCell>
                      <TableCell>{crew.gender}</TableCell>
                      <TableCell>{crew.nationality}</TableCell>
                      <TableCell className="text-xs">{crew.languages.join(", ")}</TableCell>
                      <TableCell className="text-xs">
                        {crew.dish_recipes ? (
                          <div className="space-y-1">
                            <div className="font-semibold">Recipes:</div>
                            {crew.dish_recipes.map((recipe, idx) => (
                              <div key={idx}>• {recipe}</div>
                            ))}
                          </div>
                        ) : (
                          "-"
                        )}
                      </TableCell>
                      <TableCell className="font-mono text-xs">{crew.seat_number}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>

            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <h4 className="font-semibold text-purple-900 mb-2">Cabin Crew Requirements</h4>
              <div className="text-sm text-purple-800 space-y-1">
                <div>✓ 1-4 Chief attendants required</div>
                <div>✓ 4-16 Regular attendants required</div>
                <div>✓ 0-2 Chefs allowed (optional)</div>
                <div>✓ Each chef adds special dishes to the flight menu</div>
              </div>
            </div>
          </TabsContent>

          {/* Passengers Tab */}
          <TabsContent value="passengers" className="space-y-4">
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Passport</TableHead>
                    <TableHead>Class</TableHead>
                    <TableHead>Seat</TableHead>
                    <TableHead>Age</TableHead>
                    <TableHead>Gender</TableHead>
                    <TableHead>Nationality</TableHead>
                    <TableHead>Special Notes</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {flight.passengers.map((passenger) => (
                    <TableRow key={passenger.id}>
                      <TableCell className="font-medium">{passenger.name}</TableCell>
                      <TableCell className="font-mono text-xs">{passenger.passport_number}</TableCell>
                      <TableCell>
                        <Badge variant={passenger.seat_type === "Business" ? "default" : "outline"}>
                          {passenger.seat_type}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-mono text-xs">
                        {passenger.seat_number || (passenger.parent_id ? "Infant" : "Not Assigned")}
                      </TableCell>
                      <TableCell>{passenger.age}</TableCell>
                      <TableCell>{passenger.gender}</TableCell>
                      <TableCell>{passenger.nationality}</TableCell>
                      <TableCell className="text-xs">
                        {passenger.parent_id && <Badge variant="secondary">Infant (No Seat)</Badge>}
                        {passenger.affiliated_passengers && passenger.affiliated_passengers.length > 0 && (
                          <Badge variant="outline">Group Travel</Badge>
                        )}
                        {!passenger.seat_number && !passenger.parent_id && (
                          <Badge variant="destructive">Seat Pending</Badge>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h4 className="font-semibold text-green-900 mb-2">Passenger Statistics</h4>
                <div className="text-sm text-green-800 space-y-1">
                  <div>
                    Business Class: {flight.passengers.filter((p) => p.seat_type === "Business").length}
                  </div>
                  <div>
                    Economy Class: {flight.passengers.filter((p) => p.seat_type === "Economy").length}
                  </div>
                  <div>Infants (0-2 years): {flight.passengers.filter((p) => p.age <= 2).length}</div>
                  <div>
                    Seats Assigned:{" "}
                    {flight.passengers.filter((p) => p.seat_number && !p.parent_id).length}
                  </div>
                </div>
              </div>

              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                <h4 className="font-semibold text-amber-900 mb-2">Seat Assignment Info</h4>
                <div className="text-sm text-amber-800 space-y-1">
                  <div>✓ Infants (0-2) do not require seats</div>
                  <div>✓ Affiliated passengers get neighboring seats</div>
                  <div>✓ System auto-assigns unassigned seats</div>
                  <div>✓ Preferences considered when possible</div>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
