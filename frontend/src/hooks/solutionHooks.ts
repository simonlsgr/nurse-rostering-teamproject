import { useSolution, useSolutionsArray } from "@/store/solutionStore";
import { Solution } from "@/types/nurseVars";
import solutionData from "@/components/layout/solution_instance_2.json";
import solutionData2 from "@/components/layout/solution_instance_2_infeasible.json";


export function useLoadSolutionsArray() {
  const setSolutions = useSolutionsArray((s) => s.setSolutions);
  const loadActiveSolution = useSolution((s) => s.loadSolution);

  const loadSolutionsArray = async () => {
    const id0 = "S2qch56A0c-f4WWft2L_-";
    const id1 = "v66jyIVBwd0rSYYoYenfk";
    const id2 = "MBLnJt4PxejwG5Cw2kbxC";

    const empty = {} as Solution;
    const data1 = solutionData as unknown as Solution;
    const data2 = solutionData2 as unknown as Solution;

    const solutions = [
      { solutionId: id0, solution_name: "Empty Solution", solution: empty },
      { solutionId: id1, solution_name: "Feasible Solution", solution: data1 },
      { solutionId: id2, solution_name: "Infeasible Solution", solution: data2 },
    ];

    setSolutions(solutions);


    const activeId = useSolution.getState().solutionId;
    if (!activeId) {
      const first = solutions[0];
      loadActiveSolution(first.solutionId, first.solution_name, first.solution);
    }
  };

  return { loadSolutionsArray };
}