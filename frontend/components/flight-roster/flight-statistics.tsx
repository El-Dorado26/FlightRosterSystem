"use client";

import { Flight } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, UserCheck, PlaneTakeoff, TrendingUp } from "lucide-react";

interface FlightStatisticsProps {
  flight: Flight;
}

export function FlightStatistics({ flight }: FlightStatisticsProps) {
  const totalCapacity = flight.vehicle_type.total_seats || 0;
  const occupiedSeats = flight.passengers.filter((p) => !p.parent_id).length;
  const occupancyRate = Math.round((occupiedSeats / totalCapacity) * 100);

  const businessSeats = flight.passengers.filter((p) => p.seat_type === "business" && !p.parent_id).length;
  const economySeats = flight.passengers.filter((p) => p.seat_type === "economy" && !p.parent_id).length;
  const infantCount = flight.passengers.filter((p) => p.parent_id).length;

  const businessCapacity = flight.vehicle_type.seating_plan?.business || 16;
  const economyCapacity = flight.vehicle_type.seating_plan?.economy || 150;

  const businessOccupancy = businessCapacity > 0 ? Math.round((businessSeats / businessCapacity) * 100) : 0;
  const economyOccupancy = economyCapacity > 0 ? Math.round((economySeats / economyCapacity) * 100) : 0;

  const totalCrew = flight.flight_crew.length + flight.cabin_crew.length;
  const seniorPilots = flight.flight_crew.filter((c) => c.seniority_level === "senior").length;
  const chiefAttendants = flight.cabin_crew.filter((c) => c.attendant_type === "chief").length;
  const chefs = flight.cabin_crew.filter((c) => c.attendant_type === "chef").length;

  const stats = [
    {
      title: "Overall Occupancy",
      value: `${occupiedSeats}/${totalCapacity}`,
      percentage: occupancyRate,
      icon: Users,
      color: "text-blue-600",
    },
    {
      title: "Business Class",
      value: `${businessSeats}/${businessCapacity}`,
      percentage: businessOccupancy,
      icon: TrendingUp,
      color: "text-purple-600",
    },
    {
      title: "Economy Class",
      value: `${economySeats}/${economyCapacity}`,
      percentage: economyOccupancy,
      icon: Users,
      color: "text-green-600",
    },
    {
      title: "Total Crew",
      value: `${totalCrew}`,
      percentage: 100,
      icon: UserCheck,
      color: "text-orange-600",
    },
  ];

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <Card key={index}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
                <Icon className={`h-4 w-4 ${stat.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${stat.color} bg-current transition-all`}
                    style={{ width: `${stat.percentage}%` }}
                  />
                </div>
                <p className="text-xs text-muted-foreground mt-1">{stat.percentage}% capacity</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Crew Breakdown</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Flight Crew:</span>
              <div className="flex items-center gap-2">
                <PlaneTakeoff className="h-4 w-4 text-blue-600" />
                <span className="font-semibold">{flight.flight_crew.length}</span>
                <span className="text-xs text-muted-foreground">
                  ({seniorPilots} Senior)
                </span>
              </div>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Cabin Crew:</span>
              <div className="flex items-center gap-2">
                <UserCheck className="h-4 w-4 text-purple-600" />
                <span className="font-semibold">{flight.cabin_crew.length}</span>
                <span className="text-xs text-muted-foreground">
                  ({chiefAttendants} Chief, {chefs} Chef)
                </span>
              </div>
            </div>
            <div className="flex items-center justify-between text-sm pt-2 border-t">
              <span className="text-muted-foreground">Infants (No Seat):</span>
              <span className="font-semibold">{infantCount}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Available Seats:</span>
              <span className="font-semibold text-green-600">{totalCapacity - occupiedSeats}</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {flight.shared_flight_info && (
        <Card className="border-amber-200 bg-amber-50">
          <CardHeader>
            <CardTitle className="text-sm text-amber-900">Shared Flight</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-amber-800">
            <div className="space-y-1">
              <div>
                <strong>Partner Airline:</strong> {flight.shared_flight_info.secondary_airline?.airline_name || 'N/A'}
              </div>
              <div>
                <strong>Partner Flight #:</strong> {flight.shared_flight_info.secondary_flight_number}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
