import { Solution } from "@/types/nurseVars";
import { create } from "zustand";

export type SolutionEntry = {
  solutionId: string;
  solution_name: string;
  solution: Solution;
};

// currently active solution within a project
type ActiveSolutionState = {
  solutionId: string;
  solution_name: string;
  solution: Solution | null;
  setSolution: (solution: Solution) => void;
  setSolutionName: (name: string) => void;
  setSolutionId: (id: string) => void;
  loadSolution: (id: string, solution_name: string, solution: Solution) => void;
};

export const useSolution = create<ActiveSolutionState>((set) => ({
  solutionId: "",
  solution_name: "",
  solution: null,
  setSolution: (solution) => set({ solution }),
  setSolutionName: (solution_name) => set({ solution_name }),
  setSolutionId: (solutionId) => set({ solutionId }),
  loadSolution: (solutionId, solution_name, solution) =>
    set({ solutionId, solution_name, solution }),
}));

type SolutionsArrayState = {
  solutions: SolutionEntry[];
  setSolutions: (solutions: SolutionEntry[]) => void;
  addSolution: (entry: SolutionEntry) => void;
  clearSolutions: () => void;
};

export const useSolutionsArray = create<SolutionsArrayState>((set) => ({
  solutions: [],
  setSolutions: (solutions) => set({ solutions }),
  addSolution: (entry) =>
    set((state) => ({ solutions: [...state.solutions, entry] })),
  clearSolutions: () => set({ solutions: [] }),
}));