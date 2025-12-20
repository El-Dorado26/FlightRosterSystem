"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Loader2, Users, AlertCircle, CheckCircle2, PlaneTakeoff, UserCheck } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface CrewSelectorProps {
  flightId: number;
  onCrewSelected: (flightCrewIds: number[], cabinCrewIds: number[]) => void;
  initialFlightCrewIds?: number[];
  initialCabinCrewIds?: number[];
}

interface FlightCrewMember {
  id: number;
  name: string;
  role: string;
  seniority_level: string;
  certifications: string[];
  languages: string[];
  qualified: boolean;
  age: number;
  nationality: string;
  license_number: string;
}

interface CabinCrewMember {
  id: number;
  name: string;
  attendant_type: string;
  languages: string[];
  recipes?: string[];
  vehicle_restrictions: number[] | null;
  qualified: boolean;
  age: number;
  nationality: string;
  employee_id: string;
}

export function CrewSelector({ flightId, onCrewSelected, initialFlightCrewIds = [], initialCabinCrewIds = [] }: CrewSelectorProps) {
  const [flightCrew, setFlightCrew] = useState<FlightCrewMember[]>([]);
  const [cabinCrew, setCabinCrew] = useState<CabinCrewMember[]>([]);
  const [selectedFlightCrewIds, setSelectedFlightCrewIds] = useState<Set<number>>(new Set(initialFlightCrewIds));
  const [selectedCabinCrewIds, setSelectedCabinCrewIds] = useState<Set<number>>(new Set(initialCabinCrewIds));
  const [loading, setLoading] = useState(true);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);

  useEffect(() => {
    fetchAvailableCrew();
  }, [flightId]);

  useEffect(() => {
    validateSelection();
    onCrewSelected(Array.from(selectedFlightCrewIds), Array.from(selectedCabinCrewIds));
  }, [selectedFlightCrewIds, selectedCabinCrewIds]);

  const fetchAvailableCrew = async () => {
    try {
      setLoading(true);
      const [flightCrewResponse, cabinCrewResponse] = await Promise.all([
        fetch(`${API_URL}/roster/available-flight-crew/${flightId}`),
        fetch(`${API_URL}/roster/available-cabin-crew/${flightId}`)
      ]);

      if (flightCrewResponse.ok) {
        const data = await flightCrewResponse.json();
        setFlightCrew(data);
      }

      if (cabinCrewResponse.ok) {
        const data = await cabinCrewResponse.json();
        setCabinCrew(data);
      }
    } catch (error) {
      console.error('Failed to fetch available crew:', error);
    } finally {
      setLoading(false);
    }
  };

  const validateSelection = () => {
    const errors: string[] = [];
    const selectedFlightCrew = flightCrew.filter(c => selectedFlightCrewIds.has(c.id));
    const selectedCabinCrew = cabinCrew.filter(c => selectedCabinCrewIds.has(c.id));

    // Flight Crew validation
    const roles = selectedFlightCrew.map(c => c.role);
    const seniority = selectedFlightCrew.map(c => c.seniority_level);

    if (!roles.includes('Captain')) {
      errors.push("Must select at least one Captain");
    }
    if (!roles.includes('First Officer')) {
      errors.push("Must select at least one First Officer");
    }
    if (!seniority.includes('Senior') && !seniority.includes('senior')) {
      errors.push("Must have at least one Senior pilot");
    }
    if (!seniority.includes('Junior') && !seniority.includes('junior') && 
        !seniority.includes('Intermediate') && !seniority.includes('intermediate')) {
      errors.push("Must have at least one Junior or Intermediate pilot");
    }
    
    const traineeCount = seniority.filter(s => s === 'Trainee' || s === 'trainee').length;
    if (traineeCount > 2) {
      errors.push(`Too many trainee pilots (max 2, selected ${traineeCount})`);
    }

    // Cabin Crew validation
    const cabinTypes = selectedCabinCrew.map(c => c.attendant_type);
    const chiefCount = cabinTypes.filter(t => t === 'chief').length;
    const regularCount = cabinTypes.filter(t => t === 'regular').length;
    const chefCount = cabinTypes.filter(t => t === 'chef').length;

    if (chiefCount < 1 || chiefCount > 4) {
      errors.push(`Need 1-4 Chief attendants (selected ${chiefCount})`);
    }
    if (regularCount < 4 || regularCount > 16) {
      errors.push(`Need 4-16 Regular attendants (selected ${regularCount})`);
    }
    if (chefCount > 2) {
      errors.push(`Maximum 2 Chefs allowed (selected ${chefCount})`);
    }

    setValidationErrors(errors);
  };

  const toggleFlightCrew = (crewId: number) => {
    setSelectedFlightCrewIds(prev => {
      const newSet = new Set(prev);
      if (newSet.has(crewId)) {
        newSet.delete(crewId);
      } else {
        newSet.add(crewId);
      }
      return newSet;
    });
  };

  const toggleCabinCrew = (crewId: number) => {
    setSelectedCabinCrewIds(prev => {
      const newSet = new Set(prev);
      if (newSet.has(crewId)) {
        newSet.delete(crewId);
      } else {
        newSet.add(crewId);
      }
      return newSet;
    });
  };

  const selectByRole = (role: string) => {
    const qualifiedCrew = flightCrew
      .filter(c => c.role === role && c.qualified)
      .sort((a, b) => {
        const seniority = { 'Senior': 3, 'senior': 3, 'Intermediate': 2, 'intermediate': 2, 'Junior': 1, 'junior': 1, 'Trainee': 0, 'trainee': 0 };
        return (seniority[b.seniority_level as keyof typeof seniority] || 0) - (seniority[a.seniority_level as keyof typeof seniority] || 0);
      });
    
    if (qualifiedCrew.length > 0) {
      setSelectedFlightCrewIds(prev => new Set([...prev, qualifiedCrew[0].id]));
    }
  };

  const selectByType = (type: string, count: number) => {
    const qualifiedCrew = cabinCrew.filter(c => c.attendant_type === type && c.qualified);
    const toSelect = qualifiedCrew.slice(0, count);
    
    setSelectedCabinCrewIds(prev => {
      const newSet = new Set(prev);
      toSelect.forEach(c => newSet.add(c.id));
      return newSet;
    });
  };

  const quickSelect = () => {
    // Quick select recommended crew
    selectByRole('Captain');
    selectByRole('First Officer');
    selectByRole('Flight Engineer');
    selectByType('chief', 2);
    selectByType('regular', 8);
    selectByType('chef', 1);
  };

  const clearSelection = () => {
    setSelectedFlightCrewIds(new Set());
    setSelectedCabinCrewIds(new Set());
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        <span className="ml-3 text-gray-600">Loading available crew...</span>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Validation Status */}
      {validationErrors.length > 0 ? (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            <div className="font-semibold mb-1">Selection Requirements Not Met:</div>
            <ul className="list-disc list-inside space-y-1">
              {validationErrors.map((error, idx) => (
                <li key={idx} className="text-sm">{error}</li>
              ))}
            </ul>
          </AlertDescription>
        </Alert>
      ) : (
        <Alert className="border-green-200 bg-green-50">
          <CheckCircle2 className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">
            <strong>Crew selection valid!</strong> All requirements met.
          </AlertDescription>
        </Alert>
      )}

      {/* Quick Actions */}
      <div className="flex gap-2">
        <Button onClick={quickSelect} variant="outline" size="sm">
          <Users className="h-4 w-4 mr-2" />
          Quick Select Recommended
        </Button>
        <Button onClick={clearSelection} variant="outline" size="sm">
          Clear All
        </Button>
        <div className="ml-auto text-sm text-gray-600 flex items-center gap-4">
          <span>Flight Crew: <strong>{selectedFlightCrewIds.size}</strong></span>
          <span>Cabin Crew: <strong>{selectedCabinCrewIds.size}</strong></span>
        </div>
      </div>

      <Tabs defaultValue="flight-crew" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="flight-crew">
            <PlaneTakeoff className="h-4 w-4 mr-2" />
            Flight Crew ({flightCrew.length} available)
          </TabsTrigger>
          <TabsTrigger value="cabin-crew">
            <UserCheck className="h-4 w-4 mr-2" />
            Cabin Crew ({cabinCrew.length} available)
          </TabsTrigger>
        </TabsList>

        {/* Flight Crew Tab */}
        <TabsContent value="flight-crew" className="space-y-2">
          <div className="text-sm text-gray-600 mb-3 p-3 bg-blue-50 rounded-lg">
            <strong>Requirements:</strong> 1 Captain, 1 First Officer, 1+ Senior, 1+ Junior/Intermediate, Max 2 Trainees
          </div>
          
          <div className="space-y-2 overflow-y-auto" style={{ maxHeight: 'calc(100vh - 400px)' }}>
            {flightCrew.map((crew) => (
              <Card
                key={crew.id}
                className={`cursor-pointer transition-all ${
                  selectedFlightCrewIds.has(crew.id)
                    ? 'border-blue-500 bg-blue-50'
                    : crew.qualified
                    ? 'hover:border-gray-400'
                    : 'opacity-60 border-red-200'
                }`}
                onClick={() => crew.qualified && toggleFlightCrew(crew.id)}
              >
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                      <input
                        type="checkbox"
                        checked={selectedFlightCrewIds.has(crew.id)}
                        onChange={() => {}}
                        disabled={!crew.qualified}
                        className="mt-1 h-4 w-4 rounded"
                      />
                      <div className="space-y-1">
                        <div className="font-semibold">{crew.name}</div>
                        <div className="flex gap-2 flex-wrap">
                          <Badge variant={crew.role === 'Captain' ? 'default' : 'secondary'}>
                            {crew.role}
                          </Badge>
                          <Badge variant={
                            crew.seniority_level === 'Senior' || crew.seniority_level === 'senior' ? 'default' : 'outline'
                          }>
                            {crew.seniority_level}
                          </Badge>
                          {!crew.qualified && (
                            <Badge variant="destructive">Not Qualified</Badge>
                          )}
                        </div>
                        <div className="text-xs text-gray-600">
                          Age: {crew.age} | {crew.nationality} | License: {crew.license_number}
                        </div>
                        <div className="text-xs text-gray-600">
                          Languages: {crew.languages.join(', ')}
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Cabin Crew Tab */}
        <TabsContent value="cabin-crew" className="space-y-2">
          <div className="text-sm text-gray-600 mb-3 p-3 bg-purple-50 rounded-lg">
            <strong>Requirements:</strong> 1-4 Chief, 4-16 Regular, 0-2 Chef (optional)
          </div>
          
          <div className="space-y-2 overflow-y-auto" style={{ maxHeight: 'calc(100vh - 400px)' }}>
            {cabinCrew.map((crew) => (
              <Card
                key={crew.id}
                className={`cursor-pointer transition-all ${
                  selectedCabinCrewIds.has(crew.id)
                    ? 'border-purple-500 bg-purple-50'
                    : crew.qualified
                    ? 'hover:border-gray-400'
                    : 'opacity-60 border-red-200'
                }`}
                onClick={() => crew.qualified && toggleCabinCrew(crew.id)}
              >
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                      <input
                        type="checkbox"
                        checked={selectedCabinCrewIds.has(crew.id)}
                        onChange={() => {}}
                        disabled={!crew.qualified}
                        className="mt-1 h-4 w-4 rounded"
                      />
                      <div className="space-y-1">
                        <div className="font-semibold">{crew.name}</div>
                        <div className="flex gap-2 flex-wrap">
                          <Badge variant={
                            crew.attendant_type === 'chief' ? 'default' :
                            crew.attendant_type === 'chef' ? 'secondary' : 'outline'
                          }>
                            {crew.attendant_type}
                          </Badge>
                          {!crew.qualified && (
                            <Badge variant="destructive">Vehicle Restricted</Badge>
                          )}
                        </div>
                        <div className="text-xs text-gray-600">
                          Age: {crew.age} | {crew.nationality} | ID: {crew.employee_id}
                        </div>
                        <div className="text-xs text-gray-600">
                          Languages: {Array.isArray(crew.languages) ? crew.languages.join(', ') : crew.languages}
                        </div>
                        {crew.recipes && crew.recipes.length > 0 && (
                          <div className="text-xs text-gray-600">
                            Recipes: {crew.recipes.join(', ')}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
