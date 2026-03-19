import { Solution } from "@/types/nurseVars";
import { create } from "zustand";

export type SolutionEntry = {
  solutionId: string;
  solution_name: string;
  solution: Solution;
  solver: string;
  return_status: string;
};

// currently active solution within a project
type ActiveSolutionState = {
  solutionId: string;
  solution_name: string;
  solver: string;
  return_status: string;
  solution: Solution | null;
  setSolution: (solution: Solution) => void;
  setSolutionName: (name: string) => void;
  setSolutionId: (id: string) => void;
  loadSolution: (id: string, solution_name: string, solution: Solution, solver: string, return_status: string) => void;
};

export const useSolution = create<ActiveSolutionState>((set) => ({
  solutionId: "",
  solution_name: "",
  solver: "",
  return_status: "",
  solution: null,
  setSolution: (solution) => set({ solution }),
  setSolutionName: (solution_name) => set({ solution_name }),
  setSolutionId: (solutionId) => set({ solutionId }),
  loadSolution: (solutionId, solution_name, solution, solver, return_status) =>
    set({ solutionId, solution_name, solution, solver, return_status }),
}));

type SolutionsArrayState = {
  solutions: SolutionEntry[];
  setSolutions: (solutions: SolutionEntry[]) => void;
  addSolution: (entry: SolutionEntry) => void;
  updateSolution: (solutionId: string, solution: Solution) => void;
  updateReturnStatus: (solutionId: string, return_status: string) => void;
  clearSolutions: () => void;
};

export const useSolutionsArray = create<SolutionsArrayState>((set) => ({
  solutions: [],
  setSolutions: (solutions) => set({ solutions }),
  updateSolution: (solutionId: string, solution: Solution) =>
    set((state) => ({
      solutions: state.solutions.map((s) =>
        s.solutionId === solutionId
          ? { ...s, solution } 
          : s
      ),
    })),
  updateReturnStatus: (solutionId: string, return_status: string) =>
    set((state) => ({
      solutions: state.solutions.map((s) =>
        s.solutionId === solutionId
          ? { ...s, return_status }
          : s
      ),
    })),
  addSolution: (entry) =>
    set((state) => ({ solutions: [...state.solutions, entry] })),
  clearSolutions: () => set({ solutions: [] }),
}));