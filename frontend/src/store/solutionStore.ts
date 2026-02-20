import { Solution } from "@/types/nurseVars";
import { create } from "zustand";



// currently active solution within a project
type SolutionState = {
  solutionId: string;
  solution: Solution;
  setSolution: (solution: Solution) => void;
  setSolutionId: (id: string) => void;
  loadSolution: (id: string, solution: Solution) => void;
};

export const useSolution = create<SolutionState>((set) => ({
  solutionId: "",
  solution: {},
  setSolution: (solution) => set({ solution }),
  setSolutionId: (solutionId) => set({ solutionId }),
  loadSolution: (solutionId, solution) => set({ solutionId, solution }),
}));

