import { useInstance } from "@/store/instanceStore";
import instanceData from "@/components/layout/Instance2.json";
import { getAllNurses } from "@/app/api/nurse";
import { useSelectedProject } from "@/store/projectStore";
import { Project } from "@/types/projectVars";


export function useLoadInstance(){

  const { setInstance } = useInstance();
  const { selectedProject } = useSelectedProject();

  // const loadInstance = async() => {
  //   const data = instanceData;  
    
  //   setInstance(data);
  // };

  const loadInstance = async () => {
    if (!selectedProject) return

    const data = instanceData;

    const {nurses, ...other} = data;
    
    try {
      const db_nurses = await getAllNurses(selectedProject.id);
      console.log(db_nurses);
      setInstance({nurses: db_nurses, ...other});
    } catch (err: any) {
      alert(err);
      setInstance(data);
    }

  }

  return { loadInstance };
}
