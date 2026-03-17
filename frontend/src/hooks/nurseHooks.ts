import { createNurse } from "@/app/api/nurse";
import { createDefaultNurse, generateUID } from "@/lib/utils";
import { useNewNurse, useNurses } from "@/store/nurseStore"
import { useSelectedProject } from "@/store/projectStore";



export function useHandleCreateNurse() {

  const { nurses, setNurses } = useNurses();
  const { newNurse, setNewNurse } = useNewNurse();
  const { selectedProject } = useSelectedProject();

  const handleCreateNurse = async () => {

    if ( !selectedProject ) return;

    if ( nurses.filter((nurse) => nurse.uid == newNurse.uid)[0] ){
      while (nurses.filter((nurse) => nurse.uid == newNurse.uid)[0]) {
        console.log("Regenerating UID because of collision");
        setNewNurse(prev =>({
          ...prev,
          uid: generateUID()
        }))
      }
    }

    try {
      const nurse = await createNurse(newNurse, selectedProject.id);
      setNurses(prev => [
        ...prev,
        nurse
      ]);
      setNewNurse(createDefaultNurse());

    } catch (err: any) {
      alert(err.message || "Failed to create nurse");
    }

  }

  return { handleCreateNurse }
}