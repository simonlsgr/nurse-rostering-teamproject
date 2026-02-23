
import { Instance, Nurse, Solution } from "@/types/nurseVars";
import { useInstance } from "@/store/instanceStore";
import { useFixedVars } from "@/store/fixedVarsStore"
import { use, useEffect, useMemo, useState } from "react";
import React from "react";
import { InfeasibilityDetails } from "src/types/feasibilityHelperVars";
import { NurseTable } from "../rostering/RosteringTable";
import { instanceSolutionToTableData } from "@/lib/roster/dataWrangler";
import { calculateObjective, checkFeasibility } from "@/lib/roster/modelChecker";

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
        [instance, fixedVariables]
    );

    const [fixedVariableData, setFixedVariableData] = useState<any[]>([]);
    useEffect(() => {
        console.log(fixedVariableData);
        setFixedVariableData(fixedVariableTableData);
    }, [fixedVariableTableData, instance.nurses, instance.shifts]);
    


    const [infeasibilityDetails, setInfeasibilityDetails] = useState<InfeasibilityDetails>({});


    return (
        <div className="flex flex-col gap-4">
            <div className="flex gap-4">
            <NurseTable tableData={fixedVariableData} setTableData={setFixedVariableData} instance={instance} infeasibilityDetails={infeasibilityDetails}/>
            
            </div>
            <button
                onClick={() => {
                    alert(JSON.stringify(fixedVariableData, null, 2));
                    }}
                className="w-min px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                Show Fixed Variables
            </button>
        </div>
    )
}
