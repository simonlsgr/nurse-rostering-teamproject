import { useInstance } from "@/store/instanceStore";
import instanceData from "@/components/layout/Instance2.json";
import { getAllNurses } from "@/app/api/nurse";
import { useSelectedProject } from "@/store/projectStore";


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
      setInstance({nurses: db_nurses, ...other});
    } catch (err: any) {
      alert(err);
      setInstance(data);
    }

  }

  return { loadInstance };
}
