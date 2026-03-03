import { create } from "zustand";


type SolverSettingsState = {
    activateFixedVariables: boolean;
    setactivateFixedVariables: (activate: boolean) => void;
    fixedVariablesFeasible: boolean;
    setFixedVariablesFeasible: (feasible: boolean) => void;
    usedSolver: string;
    setUsedSolver: (solver: string) => void;
    usedSolverError: boolean;
    setUsedSolverError: (solverError: boolean) => void;
    timeLimit: number;
    setTimeLimit: (timeLimit: number) => void;
}

export const useSolverSettings = create<SolverSettingsState>((set) => ({
    activateFixedVariables: false,
    setactivateFixedVariables: (activate) => set({ activateFixedVariables: activate }),
    fixedVariablesFeasible: true,
    setFixedVariablesFeasible: (feasible) => set({ fixedVariablesFeasible: feasible }),
    usedSolver: "",
    setUsedSolver: (solver) => set({ usedSolver: solver }),
    usedSolverError: false,
    setUsedSolverError: (solverError) => set({ usedSolverError: solverError }),
    timeLimit: 60,
    setTimeLimit: (timeLimit) => set({ timeLimit }),
}))