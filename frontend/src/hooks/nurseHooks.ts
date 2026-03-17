import { createDefaultNurse, generateUID } from "@/lib/utils";
import { useNewNurse, useNurses } from "@/store/nurseStore"
import { Nurse } from "@/types/nurseVars"
import { previousDay } from "date-fns";



export function useHandleCreateNurse() {

  const { nurses, setNurses } = useNurses();
  const { newNurse, setNewNurse } = useNewNurse();

  const handleCreateNurse = () => {

    if ( nurses.filter((nurse) => nurse.uid == newNurse.uid)[0] ){
      while (nurses.filter((nurse) => nurse.uid == newNurse.uid)[0]) {
        console.log("Regenerating UID because of collision");
        setNewNurse(prev =>({
          ...prev,
          uid: generateUID()
        }))
      }
    }

    setNurses(prev => [
      ...prev,
      newNurse
    ]);

    setNewNurse(createDefaultNurse());



  }

  return { handleCreateNurse }
}