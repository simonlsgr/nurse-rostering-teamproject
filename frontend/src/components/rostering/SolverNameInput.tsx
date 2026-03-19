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

    const solutionName = useSolverSettings((s) => s.solutionName);
    const editSolutionName = useSolverSettings((s) => s.editSolutionName);
    const solutionNameError = useSolverSettings((s) => s.solutionNameError);
    const [shouldShake, setShouldShake] = useState(false);
    const wasErrorRef = useRef(false);

    useEffect(() => {
        if (!wasErrorRef.current && solutionNameError) {
            setShouldShake(true);
        }
        wasErrorRef.current = solutionNameError;
    }, [solutionNameError]);

    useEffect(() => {
        if (!solutionNameError) {
            setShouldShake(false);
        }
    }, [solutionNameError]);

    function handleChange(event: SelectChangeEvent) {
        editSolutionName(event.target.value);
    }

    return (
        <div className="p-4 min-w-50 h-20">
            <motion.div
                className="w-full h-full"
                variants={shakeVariants}
                animate={shouldShake ? "error" : "idle"}
                transition={{ duration: 0.45, ease: "easeInOut" }}
                onAnimationComplete={() => shouldShake && setShouldShake(false)}
            >
                <input
                className={`border border-border h-full! rounded-md p-1  ${solutionNameError ? "border-red-500" : ""}`}
                type="text"
                inputMode="text"
                value={solutionName}
                onChange={handleChange}
                placeholder="Solution name"
                />
            </motion.div>
        </div>
    );
}
