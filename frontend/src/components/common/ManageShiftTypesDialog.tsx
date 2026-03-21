import { useEffect, useState } from "react";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "../ui/dialog";
import { Button } from "../ui/button";
import ShiftTypesEditor from "./ShiftTypesEditor";
import { useSelectedProject, useShiftTypes } from "@/store/projectStore";
import NotFollowedByShiftTypesInput from "./NotFollowedByShiftTypesInput";
import NotFollowedByShiftTypesEditor from "./NotFollowedByShiftTypesEditor";
import { ShiftType } from "@/types/projectVars";
import { createShiftType, deleteShiftType } from "@/app/api/shiftType";
import { useShifts } from "@/store/nurseStore";
import { createShift, createShifts, deleteShifts, editShift, getAllShifts } from "@/app/api/shift";
import { Shift } from "@/types/nurseVars";
import { useGenerateShifts } from "@/hooks/nurseHooks";
import { generateDatesFromPlanningHorizon } from "@/lib/utils";


export default function ManageShiftTypesDialog() {
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

  const removeConstraintFromShifts = async (shiftType: string) => {
    
    if(!selectedProject) return;

    try {

      const affectedShifts = shifts.filter((shift) => shift.not_followed_by_shift_types.includes(shiftType));

      const editedShifts: Shift[] = affectedShifts.map((shift) => {
        return {
          ...shift,
          not_followed_by_shift_types: shift.not_followed_by_shift_types.filter((type) => type !== shiftType)
        }
      });

      for (const editedShift of editedShifts) {
        const res = await editShift(editedShift, selectedProject.id);
      }

      // we do this later anyways (in handleUpdateShiftTypes)
      // const freshShifts = await getAllShifts(selectedProject.id);
      // setShifts(freshShifts);

    } catch (err: any) {
      alert(err ?? `Could not delete associated shifts of type ${shiftType}`);
    }


  }


  const handleUpdateShiftTypes = async (oldShiftTypes: ShiftType[]) => {

    if (!selectedProject) return;

    const adjustedShiftTypesIds = adjustedShiftTypes.map((shift) => shift.id);
    const oldShiftTypesIds = oldShiftTypes.map((shift) => shift.id);

    try {
      const deletedShiftTypes = oldShiftTypes.filter((shift) => !adjustedShiftTypesIds.includes(shift.id))
      const newShiftTypes = adjustedShiftTypes.filter((shift) => !oldShiftTypesIds.includes(shift.id))

      for (const shiftType of deletedShiftTypes){
        const res = await deleteShiftType(shiftType.id, selectedProject.id)
        removeShiftsOfType(shiftType.name);
        removeConstraintFromShifts(shiftType.name);
      }

      for (const shiftType of newShiftTypes) {
        const res = await createShiftType(shiftType, selectedProject.id);
      }
      const newShifts = generateShifts(generateDatesFromPlanningHorizon(selectedProject.planning_horizon), newShiftTypes);

      const res = await createShifts(newShifts, selectedProject.id);
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
            Manage Shift Types
        </Button>

      </DialogTrigger>
      <DialogContent className="!w-[48vw] !max-w-[1200px] h-[calc(80vh)]">
        <DialogHeader className="h-min">
          <DialogTitle>Manage Shift Types</DialogTitle>
        </DialogHeader>

        <div className="bg-gray-100 rounded-2xl p-3 overflow-auto flex flex-col gap-4 h-min">

          <div className="bg-white rounded-xl p-3">
            <ShiftTypesEditor actualShiftTypes={adjustedShiftTypes} setActualShiftTypes={setAdjustedShiftTypes}/>
          </div>

          <div className="bg-white rounded-xl p-3">
            <NotFollowedByShiftTypesEditor actualShiftTypes={adjustedShiftTypes} setActualShiftTypes={setAdjustedShiftTypes}  />
          </div>

        </div>





        <DialogFooter className="mt-4 flex items-end">
          <Button
            onClick={() => setOpenDialog(false)}
          >
            Cancel
          </Button>
          
          <Button 
            variant={"outline"}
            onClick={() => { handleUpdateShiftTypes(shiftTypes); setOpenDialog(false); }}
            >
            Save
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}