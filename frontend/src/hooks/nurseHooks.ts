import { createNurse } from "@/app/api/nurse";
import { createDefaultNurse, generateDatesFromPlanningHorizon, generateUID } from "@/lib/utils";
import { useNewNurse, useNurses, useShifts } from "@/store/nurseStore"
import { useSelectedProject } from "@/store/projectStore";
import { Shift } from "@/types/nurseVars";
import { Project, ShiftType } from "@/types/projectVars";



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


export function useGenerateShifts() {

  const { setShifts } = useShifts();

  const generateShifts = async (project: Project, shiftTypes: ShiftType[]) => {

    const dates = generateDatesFromPlanningHorizon(project.planning_horizon);
    let shifts_arr: Shift[] = []

    dates.forEach((date, index) => {
      shiftTypes.forEach((type) => {
        shifts_arr.push({
            id: crypto.randomUUID(),
            uid: generateUID(),
            name: index + "_" + type.name,
            start_time: date + "T" + type.start,
            end_time: date + "T" + type.end,
            demand: 0,
            type: type.name,
            not_followed_by_shift_types: type.not_followed_by_shift_types,
            weight_below_demand: 0,
            weight_above_demand: 0
          });
      });
    });

    setShifts(shifts_arr);
    
  }

  return { generateShifts }
}