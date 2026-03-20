import { FormControl, InputLabel, MenuItem, Select, SelectChangeEvent } from "@mui/material";
import { motion } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import { useSolverSettings } from "@/store/solverSettingsStore";

const shakeVariants = {
    idle: { x: 0 },
    error: {
        x: [0, -6, 6, -4, 4, 0],
    },
};

export default function SolverSelector () {

    const usedSolver = useSolverSettings((s) => s.usedSolver);
    const setUsedSolver = useSolverSettings((s) => s.setUsedSolver);
    const usedSolverError = useSolverSettings((s) => s.usedSolverError);
    const [shouldShake, setShouldShake] = useState(false);
    const wasErrorRef = useRef(false);

    useEffect(() => {
        if (!wasErrorRef.current && usedSolverError) {
            setShouldShake(true);
        }
        wasErrorRef.current = usedSolverError;
    }, [usedSolverError]);

    useEffect(() => {
        if (!usedSolverError) {
            setShouldShake(false);
        }
    }, [usedSolverError]);

    function handleChange(event: SelectChangeEvent) {
        setUsedSolver(event.target.value);
    }

    return (
        <div className="p-4 min-w-50">
            <motion.div
                className="w-full"
                variants={shakeVariants}
                animate={shouldShake ? "error" : "idle"}
                transition={{ duration: 0.45, ease: "easeInOut" }}
                onAnimationComplete={() => shouldShake && setShouldShake(false)}
            >
                <FormControl required fullWidth>
                    <InputLabel id="select-solver-label-id">Solver</InputLabel>
                    <Select
                        labelId="select-solver-label-id"
                        id="select-solver-id"
                        value={usedSolver}
                        label="Solver"
                        onChange={handleChange}
                        error={usedSolverError}
                    >
                        <MenuItem value={"cpsat-ip"}>CP SAT (IP)</MenuItem>
                        <MenuItem value={"cpsat-automaton"}>CP SAT (Automaton)</MenuItem>
                        <MenuItem value={"gurobi"}>Gurobi (IP)</MenuItem>
                        <MenuItem value={"hexaly-set"}>Hexaly (Set-Based)</MenuItem>
                        <MenuItem value={"hexaly-ip"}>Hexaly (IP)</MenuItem>
                        <MenuItem value={"hexaly-table"}>Hexaly (Table-Based)</MenuItem>
                        <MenuItem value={"greedy-heuristic"}>Heuristic (Greedy)</MenuItem>
                    </Select>
                </FormControl>
            </motion.div>
        </div>
    );
}
