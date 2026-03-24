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
import { useNurses, useShifts } from "@/store/nurseStore";
import { useSolutionsArray } from "@/store/solutionStore";
import { createSolution } from "@/app/api/solutionEntry";
import { useSelectedProject } from "@/store/projectStore";


type SolverMap = Record<string, string>;

const solver_names: SolverMap = {
  "cpsat-ip": "CP SAT (IP)",
  "cpsat-automaton": "CP SAT (Automaton)",
  "gurobi": "Gurobi (IP)",
  "hexaly-set": "Hexaly (Set-Based)",
  "hexaly-ip": "Hexaly (IP)",
  "hexaly-table": "Hexaly (Table-Based)",
  "greedy-heuristic": "Heuristic (Greedy)",
};

export default function SolveButton() {


  const { jobs, setJobs } = useJobs();
  const { selectedProject } = useSelectedProject();
  const setSolverError = useSolverSettings(s => s.setUsedSolverError)
  const activateFixedVariables = useSolverSettings(s => s.activateFixedVariables);
  const fixedVariablesFeasible = useSolverSettings(s => s.fixedVariablesFeasible);
  const fixedVars = useFixedVars(s => s.solution);
  const timeLimit = useSolverSettings(s => s.timeLimit);
  const usedSolver = useSolverSettings(s => s.usedSolver);
  const nurses = useNurses(s => s.nurses);
  const shifts = useShifts(s => s.shifts);
  const staff_weight = useInstance(s => s.staff_weight);
  const solutionName = useSolverSettings(s => s.solutionName);
  const setSolutionNameError = useSolverSettings(s => s.setSolutionNameError);

  const addSolution = useSolutionsArray((s) => s.addSolution);
  

  const instance: NurseRosteringInstance = {nurses, shifts, staff_weight};



  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSolve() {
    if(!selectedProject) return;
    try {

      setLoading(true);
      setError(null);
      if (usedSolver !== "" && solutionName != "") {
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

        payload["webhook_url"] = "http://host.docker.internal:3000/api/webhooks/job_status"
        
        
        const data = await solve(payload)
        setResult(data);
        const sol = { solutionId: data.task_id, solution_name: solutionName, solution: {}, solver: solver_names[usedSolver], return_status: "TBD" }
        addSolution(sol);
        const res = await createSolution(sol, selectedProject.id);
        setJobs({
          ...jobs,
          [data.task_id]: {...data, name: solutionName}
        })
      } else if (solutionName !== "") {
        setSolverError(true);
      } else if (usedSolver !== "") {
        setSolutionNameError(true);
      } else {
        setSolutionNameError(true);
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
      <div className="p-4 flex">
      <Button
        className="bg-gray-800 text-white rounded-2xl h-10 w-100 text-lg"
        onClick={handleSolve}
        disabled={loading}
      >
        {loading ? "Solving..." : "Solve"}
      </Button>
      {error && <p className="text-red-600 mt-2">{error}</p>}
      {/* {result && (
        <pre className="mt-4 bg-gray-100 p-2 rounded overflow-auto">
          {JSON.stringify(result, null, 2)}
        </pre>
      )} */}
    </div>
    </div>

  );
}
