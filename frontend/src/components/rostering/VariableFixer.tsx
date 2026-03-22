
import { Instance, Nurse, Solution } from "@/types/nurseVars";
import { useInstance } from "@/store/instanceStore";
import { useFixedVars } from "@/store/fixedVarsStore"
import { useSolverSettings } from "@/store/solverSettingsStore";
import { use, useEffect, useMemo, useState } from "react";
import { InfeasibilityDetails } from "src/types/feasibilityHelperVars";
import { NurseTable } from "@/components/rostering/RosteringTable";
import { instanceSolutionToTableData } from "@/lib/roster/dataWrangler";
import { checkMaxConstraintsFeasibility } from "@/lib/roster/modelChecker";
import { getShiftByDateAndType } from "@/lib/roster/dataWrangler";
import FixVariablesSelections from "./FixVariablesSelection";
import SolverSelector from "@/components/rostering/SolverSelector";
import TimeLimitInput from "@/components/rostering/TimeLimitInput";
import SolveButton from "@/components/rostering/SolveButton";
import { useNurses, useShifts } from "@/store/nurseStore";
import SolverNameInput from "@/components/rostering/SolverNameInput";

export function VariableFixer() {

    const nurses = useNurses((s) => s.nurses);
    const shifts = useShifts((s) => s.shifts);
    const instance = useMemo(
        () => ({ nurses, shifts, staff_weight: 1 } as Instance),
        [nurses, shifts]
    );

    
    const setFixedVariables = useFixedVars((s) => s.setSolution);
    const fixedVariables = useFixedVars((s) => s.solution);

    const fixedVariableTableData = useMemo(
        () => instanceSolutionToTableData({ instance, solution: fixedVariables }),
        [instance]
    );

    const [fixedVariableData, setFixedVariableData] = useState<any[]>([]);
    useEffect(() => {
        setFixedVariableData(fixedVariableTableData);
    }, [fixedVariableTableData, instance]);

    const feasible = useSolverSettings((s) => s.fixedVariablesFeasible);
    const setFeasible = useSolverSettings((s) => s.setFixedVariablesFeasible);
    const [infeasibilityDetails, setInfeasibilityDetails] = useState<InfeasibilityDetails>({});

    useEffect(() => {
        checkMaxConstraintsFeasibility(instance, fixedVariables, setInfeasibilityDetails, setFeasible);
    }, [instance, fixedVariables]);


    useEffect(() => {
        setFixedVariablesToFixedVariableData(fixedVariableData, instance);
    }, [fixedVariableData, instance]);

    function setFixedVariablesToFixedVariableData(data: any[], instance: Instance) {
        const solution: Solution = {};
        data.forEach((row) => {
            const nurseUid = parseInt(row["Nurse"]);
            Object.keys(row).forEach((key) => {
                if (key !== "Nurse" && row[key]) {
                    
                    const shift = getShiftByDateAndType({ instance, date: key, type: row[key] });
                    if (shift) {
                        if (!solution[shift.uid]) {
                            solution[shift.uid] = [];
                        }
                        solution[shift.uid].push(nurseUid);
                    }
                }
            });
        });
        setFixedVariables(solution);
    }

    

    return (
        <div className="flex flex-col gap-4">
            <h1 className="text-2xl font-bold pb-2 mb-4 border-b border-border">
                Solve the instance
            </h1>
            <FixVariablesSelections />
            <div className="flex gap-4 max-h-[40vh]">
            <NurseTable tableData={fixedVariableData} setTableData={setFixedVariableData} instance={instance} infeasibilityDetails={infeasibilityDetails}/>
            </div>
            {/* <p>{feasible ? "feasible" : "infeasible"}</p>
            <p>{JSON.stringify(fixedVariables)}</p> */}
            <div className="rounded-2xl bg-gray-100 p-3">

              <div className="bg-white rounded-xl p-2">
                <p className="text-xl font-semibold p-2 w-60 border-b border-border"> Enter solver parameters: </p>
                <div className="flex flex-row gap-5 items-end">
                    <SolverNameInput />
                    <SolverSelector />
                    <TimeLimitInput />
                </div>
                <SolveButton />
              </div>
            </div>

        </div>
    )
}
