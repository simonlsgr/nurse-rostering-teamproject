import { Solution } from "@/types/nurseVars";
import { create } from "zustand";



// currently fixed vars in an instance within a project
type FixedVarsState = {
  solutionId: string;
  solution: Solution;
  setSolution: (solution: Solution) => void;
  setSolutionId: (id: string) => void;
  loadSolution: (id: string, solution: Solution) => void;
};

export const useFixedVars = create<FixedVarsState>((set) => ({
  solutionId: "",
  solution: {},
  setSolution: (solution) => set({ solution }),
  setSolutionId: (solutionId) => set({ solutionId }),
  loadSolution: (solutionId, solution) => set({ solutionId, solution }),
}));

