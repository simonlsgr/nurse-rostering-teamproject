"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useInstance } from "@/store/instanceStore";
import { useFixedVars } from "@/store/fixedVarsStore";
import { NurseRosteringInstance } from "@/types/solverVars";
import { useSolverSettings } from "@/store/solverSettingsStore";
import { solve } from "@/app/api/solver";
import { useJobs } from "@/store/solverStore";
import JobsList from "./JobsList";


export default function SolveButton() {


  const { jobs, setJobs } = useJobs();
  
  const activateFixedVariables = useSolverSettings(s => s.activateFixedVariables);
  const fixedVars = useFixedVars(s => s.solution);
  const timeLimit = useSolverSettings(s => s.timeLimit);
  const usedSolver = useSolverSettings(s => s.usedSolver);
  const nurses = useInstance(s => s.nurses);
  const shifts = useInstance(s => s.shifts);
  const staff_weight = useInstance(s => s.staff_weight);

  const instance: NurseRosteringInstance = {nurses, shifts, staff_weight};



  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSolve() {

    try {

      setLoading(true);
      setError(null);

      const payload: Record<string, any> = {};
      payload["nurse_rostering_instance"] = instance;
      payload["optimization_parameters"] = {};
      payload["optimization_parameters"]["timeout"] = timeLimit;
      payload["fixed_variables"] = {};
      if (activateFixedVariables) {
        payload["fixed_variables"]["active"] = fixedVars;
      } else {
        payload["fixed_variables"]["active"] = {};
      }
      payload["solver"] = usedSolver;

      
      console.log(payload)

      const data = await solve(payload)
      setResult(data);
      setJobs({
        ...jobs,
        [data.task_id]: data
      })

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
        className="mt-2 px-4 py-2 bg-gray-800 text-white rounded"
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
