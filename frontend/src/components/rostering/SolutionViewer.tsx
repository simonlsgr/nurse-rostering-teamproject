import { Instance, Nurse, Solution } from "@/types/nurseVars";
import { useInstance } from "@/store/instanceStore";
import { useSolution } from "@/store/solutionStore";
import { useFixedVars } from "@/store/fixedVarsStore"
import { use, useEffect, useMemo, useState } from "react";
import { Tooltip } from "@mui/material"
import React from "react";
import { InfeasibilityDetails } from "src/types/feasibilityHelperVars";
import { NurseTable } from "../rostering/RosteringTable";
import { instanceSolutionToTableData } from "@/lib/roster/dataWrangler";
import { calculateObjective, checkFeasibility } from "@/lib/roster/modelChecker";




export function SolutionViewer() {

    const nurses = useInstance((s) => s.nurses);
    const shifts = useInstance((s) => s.shifts);
    const instance = useMemo(
        () => ({ nurses, shifts, staff_weight: 1 } as Instance),
        [nurses, shifts]
    );




    // used to display the solution
    const solutionId = useSolution((s) => s.solutionId);
    const solution = useSolution((s) => s.solution);
    const setSolution = useSolution((s) => s.setSolution);



    const [infeasibilityDetails, setInfeasibilityDetails] = useState<InfeasibilityDetails>({});

    const tableDataFromSolution = useMemo(
        () => instanceSolutionToTableData({ instance, solution }),
        [instance, solutionId]
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
        const newObjective = calculateObjective(instance, solution);
        checkFeasibility(instance, solution, setInfeasibilityDetails, setFeasible);
        setSolutionValue(newObjective);
    }, [instance, solution]);






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

        setSolution(newSolution);

    }

    return (
        <div className="flex flex-col gap-4">
            <div className="flex gap-4">
                <NurseTable tableData={solutionData} setTableData={setSolutionData} instance={instance} infeasibilityDetails={infeasibilityDetails} />
            </div>
            <div className="flex justify-end">
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
        </div>

    )
}