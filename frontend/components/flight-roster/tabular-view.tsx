"use client";

import { Flight } from "@/lib/types";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Users } from "lucide-react";

interface TabularViewProps {
  flight: Flight;
}

export function TabularView({ flight }: TabularViewProps) {
  // Combine all people into a single list
  const flightCrew = flight.flight_crew || [];
  const cabinCrew = flight.cabin_crew || [];
  const passengers = flight.passengers || [];

  const allPeople = [
    ...flightCrew.map((crew: any) => ({
      type: "Flight Crew",
      name: crew.name,
      id: crew.employee_id,
      role: crew.role || "Pilot",
      seniority: crew.seniority_level || "-",
      seat: crew.seat_number || "-",
      age: crew.age,
      nationality: crew.nationality,
      languages: Array.isArray(crew.languages) ? crew.languages.join(", ") : crew.languages || "-",
    })),
    ...cabinCrew.map((crew: any) => ({
      type: "Cabin Crew",
      name: crew.name,
      id: crew.employee_id,
      role: crew.attendant_type || "Attendant",
      seniority: "-",
      seat: crew.seat_number || "-",
      age: crew.age,
      nationality: crew.nationality,
      languages: Array.isArray(crew.languages) ? crew.languages.join(", ") : crew.languages || "-",
    })),
    ...passengers.map((passenger: any) => ({
      type: "Passenger",
      name: passenger.name,
      id: passenger.passport_number,
      role: passenger.seat_type || passenger.class || "Economy",
      seniority: "-",
      seat: passenger.seat_number || (passenger.parent_id ? "Infant (No Seat)" : "Not Assigned"),
      age: passenger.age,
      nationality: passenger.nationality,
      languages: "-",
    })),
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Users className="h-5 w-5" />
          Tabular View - All Personnel
        </CardTitle>
        <CardDescription>
          Summary of all people on board Flight {flight.flight_number}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Type</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>ID</TableHead>
                <TableHead>Role/Class</TableHead>
                <TableHead>Seat</TableHead>
                <TableHead>Age</TableHead>
                <TableHead>Nationality</TableHead>
                <TableHead>Languages</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {allPeople.map((person, index) => (
                <TableRow key={index}>
                  <TableCell>
                    <Badge
                      variant={
                        person.type === "Flight Crew"
                          ? "default"
                          : person.type === "Cabin Crew"
                          ? "secondary"
                          : "outline"
                      }
                    >
                      {person.type}
                    </Badge>
                  </TableCell>
                  <TableCell className="font-medium">{person.name}</TableCell>
                  <TableCell className="font-mono text-xs">{person.id}</TableCell>
                  <TableCell>{person.role}</TableCell>
                  <TableCell className="font-mono text-xs">{person.seat}</TableCell>
                  <TableCell>{person.age}</TableCell>
                  <TableCell>{person.nationality}</TableCell>
                  <TableCell className="text-xs">{person.languages}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        <div className="mt-4 flex gap-4 text-sm">
          <div>
            <span className="font-semibold">Total:</span> {allPeople.length}
          </div>
          <div>
            <span className="font-semibold">Flight Crew:</span> {flight.flight_crew.length}
          </div>
          <div>
            <span className="font-semibold">Cabin Crew:</span> {flight.cabin_crew.length}
          </div>
          <div>
            <span className="font-semibold">Passengers:</span> {flight.passengers.length}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
