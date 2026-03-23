import { Instance, Nurse, Solution } from "@/types/nurseVars";
import { useInstance } from "@/store/instanceStore";
import { useSolution, useSolutionsArray } from "@/store/solutionStore";
import { useFixedVars } from "@/store/fixedVarsStore"
import { use, useEffect, useMemo, useState } from "react";
import { FormControl, InputLabel, MenuItem, Select, SelectChangeEvent, Tooltip } from "@mui/material"
import React from "react";
import { InfeasibilityDetails } from "src/types/feasibilityHelperVars";
import { NurseTable } from "../rostering/RosteringTable";
import { instanceSolutionToTableData } from "@/lib/roster/dataWrangler";
import { calculateObjective, checkFeasibility } from "@/lib/roster/modelChecker";
import { useNurses, useShifts } from "@/store/nurseStore";
import { Trash, Trash2 } from "lucide-react";

import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "../ui/dialog";
import { Button } from "../ui/button";
import { deleteSolution } from "@/app/api/solutionEntry";
import { useSelectedProject } from "@/store/projectStore";




export function SolutionViewer() {

    const nurses = useNurses((s) => s.nurses);
    const shifts = useShifts((s) => s.shifts);
    const instance = useMemo(
        () => ({ nurses, shifts, staff_weight: 1 } as Instance),
        [nurses, shifts]
    );

    const { selectedProject } = useSelectedProject();

    const [openDialog, setOpenDialog] = useState<boolean>(false);
    const [deleteId, setDeleteId] = useState<string>("");


    // used to display the solution
    const activeSolutionId = useSolution((s) => s.solutionId);
    const activeSolution = useSolution((s) => s.solution);
    const activeSolutionSolver = useSolution((s) => s.solver);
    const activeSolutionReturnStatus = useSolution((s) => s.return_status);
    const setActiveSolution = useSolution((s) => s.setSolution);
    const loadActiveSolution = useSolution((s) => s.loadSolution);
    const { solutions, setSolutions } = useSolutionsArray();



    const solutionsArray = useSolutionsArray((s) => s.solutions);

    useEffect(() => {
        if (solutionsArray.length === 0) return;
      
        const exists = solutionsArray.some(
          (s) => s.solutionId === activeSolutionId
        );
      
        if (!exists) {
          const first = solutionsArray[0];
          loadActiveSolution(first.solutionId, first.solution_name, first.solution, first.solver, first.return_status);
        }

      }, [solutionsArray, activeSolutionId, loadActiveSolution]);


    const [infeasibilityDetails, setInfeasibilityDetails] = useState<InfeasibilityDetails>({});

    const tableDataFromSolution = useMemo(
        () => instanceSolutionToTableData({ instance, solution: activeSolution ?? {} }),
        [instance, activeSolution]
    );

    const [solutionData, setSolutionData] = useState<any[]>([]);
    const isRehydratingRef = React.useRef(false);

    useEffect(() => {
        // when a new solution is selected externally, rehydrate the UI from it
        if (instance.nurses.length === 0 || instance.shifts.length === 0) return;

        isRehydratingRef.current = true;
        setSolutionData(tableDataFromSolution);
    }, [tableDataFromSolution, instance.nurses, instance.shifts]);

    useEffect(() => {

        if (isRehydratingRef.current) {
            isRehydratingRef.current = false;
            return;
        }

        updateSolutionToView();
    }, [solutionData]);

    const [feasible, setFeasible] = useState(true);
    const [solutionValue, setSolutionValue] = useState(0);

    useEffect(() => {
        const newObjective = calculateObjective(instance, activeSolution ?? {});
        checkFeasibility(instance, activeSolution ?? {}, setInfeasibilityDetails, setFeasible);
        setSolutionValue(newObjective);
    }, [instance, activeSolution]);



    const deleteSolutionEntry = async (solutionId: string) => {
      if(!selectedProject) return;
      try {

        const res = await deleteSolution(solutionId, selectedProject.id);
        setSolutions(solutions.filter((entry) => entry.solutionId !== solutionId));

      } catch (err: any) {
        alert(err ?? "Failed to delete solution");
      }
    }


    function updateSolutionToView() {

        const newSolution: Solution = {};
        for (const nurseSchedule of solutionData) {
            const nuid = Number(nurseSchedule["Nurse"]);
            for (const [date, shiftType] of Object.entries(nurseSchedule)) {
                if (date === "Nurse") continue;
                if (!shiftType) continue;

                const shift = instance.shifts.find(
                    (s) => s.type === shiftType && s.start_time.split("T")[0] === date
                );
                if (!shift) continue;

                (newSolution[shift.uid] ??= []).push(nuid);
            }
        }

        setActiveSolution(newSolution);

    }

    const handleChange = (event: SelectChangeEvent) => {
        const newSolutionId = event.target.value as string;
        const selected = solutionsArray.find((s) => s.solutionId === newSolutionId);
        if (!selected) return;
    
        loadActiveSolution(selected.solutionId, selected.solution_name, selected.solution, selected.solver, selected.return_status);
        
    };

    return (
        <div className="flex flex-col gap-4">
            <h1 className="text-2xl font-bold pb-2 mb-4 border-b border-border">
                Solutions
            </h1>
            <div className="flex gap-2">
                <FormControl>
                <InputLabel id="select-solution-label-id">Solution</InputLabel>
                <Select
                    labelId="select-solution-label-id"
                    id="select-solution-id"
                    value={activeSolutionId}
                    label="Solution"
                    onChange={handleChange}
                >
                    
                    {solutionsArray.map((s) => (
                        <MenuItem key={s.solutionId} value={s.solutionId} className="flex gap-1 group !justify-between">
                          <p>{s.solution_name}</p> 
                          <div 
                            className={`opacity-0 group-hover:opacity-100 hover:bg-gray-200 rounded ${activeSolutionId == s.solutionId ? "hidden": ""} ${s.solution_name == "Empty Solution" ? "hidden" : ""}`}
                            onClick={(e) => {
                              e.stopPropagation();
                              setDeleteId(s.solutionId);
                              setOpenDialog(true);
                            }}
                            >
                            <Trash className="p-1" />
                          </div>
                        </MenuItem>
                    ))}
                </Select>
                </FormControl>
                <div className="flex flex-col px-2 border border-border rounded-sm justify-center">
                    <p>Solver: {activeSolutionSolver ?? "Loading..."}</p>
                    <p>Return status: {activeSolutionReturnStatus ?? "Loading..."}</p>
                </div>
            </div>
            <div className="flex gap-4 max-h-[60vh]">
                <NurseTable tableData={solutionData} setTableData={setSolutionData} instance={instance} infeasibilityDetails={infeasibilityDetails} />
            </div>
            <div className="flex justify-start">
                <p className="mr-4 self-center text-sm text-gray-600">
                    {`Objective: ${solutionValue}`}
                </p>

                {feasible ?
                    <p className="mr-4 self-center text-sm text-green-600">
                        feasible
                    </p> :
                    <p className="mr-4 self-center text-sm text-red-600">
                        infeasible
                    </p>
                }

            </div>


            <Dialog open={openDialog} onOpenChange={setOpenDialog}>

              <DialogContent className="!w-[20vw] !max-w-[1200px] h-[calc(20vh)]">
                <DialogHeader className="h-min">
                  <DialogTitle>Delete Solution</DialogTitle>
                </DialogHeader>

                <div>
                  Delete this solution?
                </div>

                <DialogFooter className="mt-4 flex items-end">
                  <Button
                    onClick={() => setOpenDialog(false)}
                  >
                    Cancel
                  </Button>

                  <Button 
                    variant={"destructive"}
                    onClick={() => {deleteSolutionEntry(deleteId); setOpenDialog(false);} }
                  >
                    Delete
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>



        </div>

    )
}