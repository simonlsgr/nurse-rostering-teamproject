import { useEffect, useState } from "react";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "../ui/dialog";
import { Button } from "../ui/button";
import ShiftTypesEditor from "./ShiftTypesEditor";
import { useSelectedProject, useShiftTypes } from "@/store/projectStore";
import NotFollowedByShiftTypesInput from "./NotFollowedByShiftTypesInput";
import NotFollowedByShiftTypesEditor from "./NotFollowedByShiftTypesEditor";
import { ShiftType } from "@/types/projectVars";
import { createShiftType, deleteShiftType, editShiftType } from "@/app/api/shiftType";
import { useShifts } from "@/store/nurseStore";
import { createShift, createShifts, deleteShifts, editShift, getAllShifts } from "@/app/api/shift";
import { Shift } from "@/types/nurseVars";
import { useGenerateShifts } from "@/hooks/nurseHooks";
import { generateDatesFromPlanningHorizon } from "@/lib/utils";


export default function ManageConstraintsDialog() {
  const [openDialog, setOpenDialog] = useState<boolean>(false);
  
  const { shiftTypes, setShiftTypes } = useShiftTypes();
  const { selectedProject } = useSelectedProject();

  const { shifts, setShifts } = useShifts();
  const { generateShifts } = useGenerateShifts();

  const [ adjustedShiftTypes, setAdjustedShiftTypes ] = useState<ShiftType[]>(shiftTypes);


  useEffect(() => {

    setAdjustedShiftTypes(shiftTypes);

  }, [shiftTypes])


  useEffect(() => {

    setAdjustedShiftTypes(shiftTypes);

  }, [openDialog])



  const removeShiftsOfType = async (shiftType: string) => {
   
    if(!selectedProject) return;

    try {

      const res = await deleteShifts(shifts.filter((shift) => shift.type == shiftType).map((s) => s.id), selectedProject.id);


    } catch (err: any) {
      alert(err ?? `Could not delete associated shifts of type ${shiftType}`);
    }

  }

  const adjustConstraintsFromShifts = async (shiftType: ShiftType) => {
    
    if(!selectedProject) return;

    try {

      const editedShifts: Shift[] = shifts.filter((s) => s.type == shiftType.name).map((shift) => {
        return {
          ...shift,
          not_followed_by_shift_types: shiftType.not_followed_by_shift_types
        }
      });

      for (const editedShift of editedShifts) {
        const res = await editShift(editedShift, selectedProject.id);
      }

    } catch (err: any) {
      alert(err ?? `Could not edit associated shifts of type ${shiftType.name}`);
    }


  }


  const handleUpdateShiftTypes = async (editedShiftTypes: ShiftType[]) => {

    if (!selectedProject) return;

    try {

      for (const shiftType of editedShiftTypes){
        const res = await editShiftType(shiftType, selectedProject.id)
        adjustConstraintsFromShifts(shiftType);
      }

      const freshShifts = await getAllShifts(selectedProject.id);
      setShifts(freshShifts);
      setShiftTypes(adjustedShiftTypes);

    } catch (err: any) {
      alert(err ?? "Failed to adjust shift types");
    }

  }



  return (
    <Dialog open={openDialog} onOpenChange={setOpenDialog}>
      <DialogTrigger asChild>

        <Button className="bg-gray-50 rounded-none border-border" variant={"outline"}>
            Edit Constraints
        </Button>

      </DialogTrigger>
      <DialogContent className="!w-[48vw] !max-w-[1200px] h-[calc(60vh)] overflow-hidden">
        <DialogHeader className="h-min">
          <DialogTitle>Edit Constraints</DialogTitle>
        </DialogHeader>

        <div className="bg-gray-100 rounded-2xl p-3 overflow-auto flex flex-col gap-4 h-[43vh]">

          <div className="bg-white rounded-xl p-3 overflow-auto">
            <NotFollowedByShiftTypesEditor actualShiftTypes={adjustedShiftTypes} setActualShiftTypes={setAdjustedShiftTypes}  />
          </div>

        </div>




        <DialogFooter className="flex items-end h-10">
          <Button
            onClick={() => setOpenDialog(false)}
          >
            Cancel
          </Button>
          
          <Button 
            variant={"outline"}
            onClick={() => { handleUpdateShiftTypes(adjustedShiftTypes); setOpenDialog(false); }}
            >
            Save
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}