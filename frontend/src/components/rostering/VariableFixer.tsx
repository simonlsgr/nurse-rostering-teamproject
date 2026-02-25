
import { Instance, Nurse, Solution } from "@/types/nurseVars";
import { useInstance } from "@/store/instanceStore";
import { useFixedVars } from "@/store/fixedVarsStore"
import { use, useEffect, useMemo, useState } from "react";
import { InfeasibilityDetails } from "src/types/feasibilityHelperVars";
import { NurseTable } from "@/components/rostering/RosteringTable";
import { instanceSolutionToTableData } from "@/lib/roster/dataWrangler";
import { checkMaxConstraintsFeasibility } from "@/lib/roster/modelChecker";
import { getShiftByDateAndType } from "@/lib/roster/dataWrangler";

export function VariableFixer() {

    const nurses = useInstance((s) => s.nurses);
    const shifts = useInstance((s) => s.shifts);
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

    const [feasible, setFeasible] = useState(true);
    const [infeasibilityDetails, setInfeasibilityDetails] = useState<InfeasibilityDetails>({});

    useEffect(() => {
        checkMaxConstraintsFeasibility(instance, fixedVariables, setInfeasibilityDetails, setFeasible);
    }, [instance, fixedVariables]);


    useEffect(() => {
        setFixedVariableDataToSolution(fixedVariableData, instance);
    }, [fixedVariableData, instance]);

    function setFixedVariableDataToSolution(data: any[], instance: Instance) {
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
            <div className="flex gap-4">
            <NurseTable tableData={fixedVariableData} setTableData={setFixedVariableData} instance={instance} infeasibilityDetails={infeasibilityDetails}/>
            
            </div>
            <button
                onClick={() => {
                    console.log(setFixedVariableDataToSolution(fixedVariableData, instance));
                    }}
                className="w-min px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                Show Fixed Variables
            </button>
            <p>{feasible ? "feasible" : "infeasible"}</p>
            <p>{JSON.stringify(fixedVariables)}</p>
        </div>
    )
}
