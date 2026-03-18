"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { useInstance } from "@/store/instanceStore";
import { useFixedVars } from "@/store/fixedVarsStore";
import { NurseRosteringInstance } from "@/types/solverVars";
import { useSolverSettings } from "@/store/solverSettingsStore";
import { solve } from "@/app/api/solver";
import { useJobs } from "@/store/solverStore";
import JobsList from "./JobsList";
import { useNurses } from "@/store/nurseStore";


export default function SolveButton() {


  const { jobs, setJobs } = useJobs();
  
  const setSolverError = useSolverSettings(s => s.setUsedSolverError)
  const activateFixedVariables = useSolverSettings(s => s.activateFixedVariables);
  const fixedVariablesFeasible = useSolverSettings(s => s.fixedVariablesFeasible);
  const fixedVars = useFixedVars(s => s.solution);
  const timeLimit = useSolverSettings(s => s.timeLimit);
  const usedSolver = useSolverSettings(s => s.usedSolver);
  const nurses = useNurses(s => s.nurses);
  const shifts = useInstance(s => s.shifts);
  const staff_weight = useInstance(s => s.staff_weight);

  const instance: NurseRosteringInstance = {nurses, shifts, staff_weight};



  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSolve() {

    try {
      console.log(nurses);
      setLoading(true);
      setError(null);
      if (usedSolver !== "") {
        setSolverError(false);
        
        
        const payload: Record<string, any> = {};
        payload["nurse_rostering_instance"] = instance;
        payload["optimization_parameters"] = {};
        payload["optimization_parameters"]["timeout"] = timeLimit;
        payload["optimization_parameters"]["nurses_at_shifts_forced"] = {};
        console.log("ActivateFixedVariables", activateFixedVariables)
        console.log("FixedVariablesFeasible", fixedVariablesFeasible)
        if (activateFixedVariables && fixedVariablesFeasible) {
          payload["optimization_parameters"]["nurses_at_shifts_forced"] = fixedVars;
        } else {
          payload["optimization_parameters"]["nurses_at_shifts_forced"] = {};
        }
        payload["solver"] = usedSolver;
        
        
        
        const data = await solve(payload)
        setResult(data);
        setJobs({
          ...jobs,
          [data.task_id]: data
        })
      } else {
        setSolverError(true);
      }

    } catch (err: any) {
      setError(err.message);
      setResult(null);

    } finally {
      setLoading(false);
    }
  }


  return (

    <div>
      <div className="p-4">
      <Button
        className="bg-gray-800 text-white rounded-2xl h-10 w-full text-lg"
        onClick={handleSolve}
        disabled={loading}
      >
        {loading ? "Solving..." : "Solve"}
      </Button>
      {error && <p className="text-red-600 mt-2">{error}</p>}
      {result && (
        <pre className="mt-4 bg-gray-100 p-2 rounded overflow-auto">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
    </div>

  );
}


{/* <Button onClick={handleSolve}> Solve </Button> */}
