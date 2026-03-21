import { useInstance } from "@/store/instanceStore";
import instanceData from "@/components/layout/Instance2.json";
import { getAllNurses } from "@/app/api/nurse";
import { useSelectedProject } from "@/store/projectStore";
import { getAllShifts } from "@/app/api/shift";
import { useNurses, useShifts } from "@/store/nurseStore";


export function useLoadInstance(){

  const { setInstance } = useInstance();
  const { selectedProject } = useSelectedProject();
  const { setNurses } = useNurses();
  const { setShifts } = useShifts();

/*    const loadInstance = async() => {
     const data = instanceData;  

     setInstance(data);
   }; */

  const loadInstance = async () => {
    if (!selectedProject) return

    const data = instanceData;

    const {nurses, shifts, ...other} = data;
    
    try {
      const db_nurses = await getAllNurses(selectedProject.id);
      const db_shifts = await getAllShifts(selectedProject.id);
      setNurses(db_nurses);
      setShifts(db_shifts);
      setInstance({nurses: db_nurses, shifts: db_shifts, ...other});
      
    } catch (err: any) {
      alert(err);
      setInstance(data);
    }

  }

  return { loadInstance };
}
