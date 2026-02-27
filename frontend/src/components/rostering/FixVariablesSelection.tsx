import { Switch, FormControlLabel } from "@mui/material";
import { useEffect, useState } from "react";
import { useSolverSettings } from "@/store/solverSettingsStore";



export default function FixVariablesSelections() {
    

    const activateFixedVarsInSolving = useSolverSettings((s) => s.activateFixedVariables);
    const setActivateFixedVarsInSolving = useSolverSettings((s) => s.setactivateFixedVariables);
    const fixedVarsInSolvingFeasible = useSolverSettings((s) => s.fixedVariablesFeasible);

    useEffect(() => {
        if (!fixedVarsInSolvingFeasible) {
            setActivateFixedVarsInSolving(false);
        }
    }, [fixedVarsInSolvingFeasible, setActivateFixedVarsInSolving]);

    return (
        <div className="p-4 pb-[0]! select-none">
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
                label="Fix assignments"
            />
        </div>
    );
}