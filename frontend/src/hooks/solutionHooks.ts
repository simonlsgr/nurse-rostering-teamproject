import { useSolution, useSolutionsArray } from "@/store/solutionStore";
import { Solution } from "@/types/nurseVars";
import solutionData from "@/components/layout/solution_instance_2.json";
import solutionData2 from "@/components/layout/solution_instance_2_infeasible.json";
import { getAllSolutions } from "@/app/api/solutionEntry";
import { useSelectedProject } from "@/store/projectStore";


export function useLoadSolutionsArray() {
  const setSolutions = useSolutionsArray((s) => s.setSolutions);
  const loadActiveSolution = useSolution((s) => s.loadSolution);

  const { selectedProject } = useSelectedProject();

  const loadSolutionsArray = async () => {
    if(!selectedProject) return;

  
    const id0 = "S2qch56A0c-f4WWft2L_-";
    const empty = {} as Solution;
    const emptySolution = { solutionId: id0, solution_name: "Empty Solution", solution: empty, solver: "-", return_status: "-"};
    try {
    
    
      const solutions = await getAllSolutions(selectedProject.id);
      
      if(!solutions) return;
      
      setSolutions([emptySolution, ...solutions]);
      
      
      const activeId = useSolution.getState().solutionId;
      console.log(activeId);
      if (!activeId) {
    
          const first = emptySolution;
          console.log(first)
          loadActiveSolution(first.solutionId, first.solution_name, first.solution, first.solver, first.return_status);
      }
    } catch (err: any) {
      alert(err ?? "Failed to load solutions");
    } 
  
  
  
  
  };




  return { loadSolutionsArray };
}