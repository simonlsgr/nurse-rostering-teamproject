import { useSolution } from "@/store/solutionStore";
import { Solution } from "@/types/nurseVars";
import solutionData from "@/components/layout/solution_instance_2.json";


function randomId() {
  console.log("Generating random ID for solution...");
  return crypto.randomUUID();

}

export function useLoadSolution() {
  const loadSolutionStore = useSolution((s) => s.loadSolution);

  const loadSolution = async () => {
    const id = randomId();
    const data = solutionData as unknown as Solution;
    loadSolutionStore(id, data);
  };

  return { loadSolution };
}