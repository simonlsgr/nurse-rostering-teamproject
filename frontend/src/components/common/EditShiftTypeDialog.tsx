
import { Pencil } from "lucide-react";
import { Button } from "../ui/button";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "../ui/dialog";
import { useEffect, useState } from "react";
import { ShiftType } from "@/types/projectVars";
import { Tooltip } from "@mui/material";
import { useSelectedProject, useShiftTypes } from "@/store/projectStore";
import { editShiftType } from "@/app/api/shiftType";
import { createShifts, deleteShifts, editShift, getAllShifts } from "@/app/api/shift";
import { useShifts } from "@/store/nurseStore";
import { Shift } from "@/types/nurseVars";
import { useGenerateShifts } from "@/hooks/nurseHooks";
import { generateDatesFromPlanningHorizon } from "@/lib/utils";


type EditDialogProps = {
  shiftType: ShiftType;
}

export function EditShiftTypeDialog ({ shiftType }: EditDialogProps) {

  const [openDialog, setOpenDialog] = useState<boolean>(false);

  const [nameInput, setNameInput] = useState<string>(shiftType.name);
  const [durationInput, setDurationInput] = useState<string>(shiftType.duration);
  
  const [newShift, setNewShift] = useState({
    name: "",
    duration: "00:00:00", 
  });

  const { shifts, setShifts } = useShifts();
  const { shiftTypes, setShiftTypes } = useShiftTypes();
  const { selectedProject } = useSelectedProject();
  const { generateShifts } = useGenerateShifts();


  const isValid =
  newShift.name.trim() !== "" &&
  newShift.duration !== "" &&
  newShift.duration !== "00:00:00" && 
  !shiftTypes.filter((s) => s.id !== shiftType.id).some((s) => s.name.toLowerCase() == newShift.name.trim().toLowerCase());


  const calculateEndTime = (duration: string) => {
    const [h, m, s] = duration.split(":").map(Number);
  
    const totalSeconds = h * 3600 + m * 60 + s;
  
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;
  
    return [
      String(hours).padStart(2, "0"),
      String(minutes).padStart(2, "0"),
      String(seconds).padStart(2, "0"),
    ].join(":");
  };


  const removeShiftsOfType = async (shiftType: string) => {
   
    if(!selectedProject) return;

    try {

      const res = await deleteShifts(shifts.filter((shift) => shift.type == shiftType).map((s) => s.id), selectedProject.id);


    } catch (err: any) {
      alert(err ?? `Could not delete associated shifts of type ${shiftType}`);
    }

  }


  const replaceConstraintFromShifts = async (shiftType: string, newShiftType: ShiftType) => {
    
    if(!selectedProject) return;

    try {

      const affectedShifts = shifts.filter((shift) => shift.not_followed_by_shift_types.includes(shiftType));

      const editedShifts: Shift[] = affectedShifts.map((shift) => {
        return {
          ...shift,
          not_followed_by_shift_types: shift.not_followed_by_shift_types.map((type) => type !== shiftType ? type : newShiftType.name)
        }
      });

      for (const editedShift of editedShifts) {
        const res = await editShift(editedShift, selectedProject.id);
      }

    } catch (err: any) {
      alert(err ?? `Could not update associated shifts of type ${shiftType}`);
    }


  }


  const handleRegenerateShifts = async (oldShiftType: ShiftType, newShiftType: ShiftType) => {
    if (!selectedProject) return;

    removeShiftsOfType(oldShiftType.name);
    const newShifts = generateShifts(generateDatesFromPlanningHorizon(selectedProject.planning_horizon), [newShiftType]);

    const res = await createShifts(newShifts, selectedProject.id);
    const freshShifts = await getAllShifts(selectedProject.id);
    setShifts(freshShifts);


  }


  const handleEditShiftType = async (oldShiftType: ShiftType) => {
    if(!selectedProject) return;

    const start = "00:00:00";
    const end = calculateEndTime(newShift.duration);
    const editedShiftType = {
      id: shiftType.id,
      not_followed_by_shift_types: shiftType.not_followed_by_shift_types,
      start: start,
      end: end,
      ...newShift
    };

    try {

      const res = await editShiftType(editedShiftType, selectedProject.id)
      const arr = shiftTypes.filter((type) => type.id !== res.id).concat([res]);
      setShiftTypes(arr);

      handleRegenerateShifts(oldShiftType, res);
      replaceConstraintFromShifts(oldShiftType.name, res);


    } catch (err: any) {
      alert(err ?? "Failed to edit shift type");
    }


  }


  useEffect(() => {

    setNameInput(shiftType.name);
    setDurationInput(shiftType.duration);
  }, [openDialog])

  useEffect(() => {

    setNewShift({name: nameInput, duration: durationInput});
  }, [nameInput, durationInput])


  return (
    <Dialog open={openDialog} onOpenChange={setOpenDialog}>
      <DialogTrigger asChild>
        
          <button
            className="text-black hover:bg-gray-100 pt-1 rounded"
          >
            <Pencil />
          </button>

      </DialogTrigger>
      <DialogContent className="w-[calc(30vw)]">
        <DialogHeader>
          <DialogTitle> Edit shift type </DialogTitle>
        </DialogHeader>

        <div className="flex gap-4">
        <input
          type="text"
          placeholder="Shift Name"
          value={nameInput}
          onChange={(e) =>
            setNameInput(e.target.value)
          }
          className="border border-border p-2 rounded"
        />
      
        <Tooltip
          title="Duration of shift"
          enterDelay={200}
          enterNextDelay={200}
        >

          <input
            type="time"
            step="1"
            value={durationInput}
            onChange={(e) =>
              setDurationInput(e.target.value)
            }
            className="border border-border p-2 rounded"
          />
        </Tooltip>

        </div>


        <DialogFooter className="mt-4">
          <Button
            onClick={() => {setOpenDialog(false);}}
          >
            Cancel
          </Button>

          <Button
            variant={"outline"}
            className={`${
            isValid ? "" : "bg-gray-300 cursor-not-allowed"
            }`}
            disabled={!isValid}
            onClick={() => {

              handleEditShiftType(shiftType);
              setNewShift({ name: "", duration: "00:00:00" });
              setOpenDialog(false);
            }}
          >
          Save
          </Button>

        </DialogFooter>
      </DialogContent>
    </Dialog>


  )
}
/* 
setShiftType({
  id: shiftType.id,
  not_followed_by_shift_types: shiftType.not_followed_by_shift_types,
  start: start,
  end: end,
  ...newShift
}); */