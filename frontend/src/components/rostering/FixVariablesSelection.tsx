import { Switch, FormControlLabel } from "@mui/material";
import { useEffect, useState } from "react";
import { useSolverSettings } from "@/store/solverSettingsStore";



export default function FixVariablesSelections() {
    

    const activateFixedVarsInSolving = useSolverSettings((s) => s.activateFixedVariables);
    const setActivateFixedVarsInSolving = useSolverSettings((s) => s.setactivateFixedVariables);
    const fixedVarsInSolvingFeasible = useSolverSettings((s) => s.fixedVariablesFeasible);
    

    useEffect(() => {
        if (!fixedVarsInSolvingFeasible && activateFixedVarsInSolving) {
            setActivateFixedVarsInSolving(true);
        }
    }, [fixedVarsInSolvingFeasible, setActivateFixedVarsInSolving]);

    return (
        <div className="select-none flex items-center">
            <FormControlLabel
                id="fix-variables-checkbox"
                control={
                    <Switch
                        disabled={!fixedVarsInSolvingFeasible}
                        checked={activateFixedVarsInSolving && fixedVarsInSolvingFeasible}
                        onChange={(event, newChecked) => {
                            setActivateFixedVarsInSolving(newChecked);
                        }}
                    />
                }
                label="Fix nurses to specific shifts."
            />
            {!fixedVarsInSolvingFeasible && <p className="text-red-600">The current assignment is already infeasible. To apply an assignment it has to be feasible.</p>}
        </div>
    );
}