import { FormControl, InputLabel, MenuItem, Select, SelectChangeEvent } from "@mui/material";
import { useSolverSettings } from "@/store/solverSettingsStore";



export default function SolverSelector () {

    const usedSolver = useSolverSettings((s) => s.usedSolver);
    const setUsedSolver = useSolverSettings((s) => s.setUsedSolver);

    function handleChange(event: SelectChangeEvent) {
        setUsedSolver(event.target.value);
    }

    return (
        <div className="p-4">
            <div>
            <FormControl required fullWidth>
            <InputLabel id="select-solver-label-id">Solver</InputLabel>
            <Select
                
                labelId="select-solver-label-id"
                id="select-solver-id"
                value={usedSolver}
                label="Solver"
                onChange={handleChange}
            >
                
                
                <MenuItem value={"cp-sat"}>CP SAT</MenuItem>
                <MenuItem value={"gurobi"}>Gurobi</MenuItem>
                <MenuItem value={"hexaly"}>Hexaly</MenuItem>
                
            </Select>
            </FormControl>
            </div>
        </div>
    );
}