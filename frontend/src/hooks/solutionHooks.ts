import { useSolution } from "@/store/solutionStore";
import { Solution } from "@/types/nurseVars";
import solutionData from "@/components/layout/solution_instance_2.json";
import { nanoid } from "nanoid";



export function useLoadSolution() {
  const loadSolutionStore = useSolution((s) => s.loadSolution);

  const loadSolution = async () => {
    const id = nanoid();
    const data = solutionData as unknown as Solution;
    loadSolutionStore(id, data);
  };

  return { loadSolution };
}