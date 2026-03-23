import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "../ui/dialog";
import { Button } from "../ui/button";
import { calculateStringDifference, formatDate, generateDatesFromPlanningHorizon } from "@/lib/utils";
import { useSelectedProject, useShiftTypes } from "@/store/projectStore";
import { useEffect, useState } from "react";
import { Project } from "@/types/projectVars";
import { editProject } from "@/app/api/project";
import { useShifts } from "@/store/nurseStore";
import { useGenerateShifts } from "@/hooks/nurseHooks";
import { createShift, createShifts, deleteShift, deleteShifts, getAllShifts } from "@/app/api/shift";


export default function ManagePlanningHorizonDialog() {
  
  const { selectedProject, setSelectedProject } = useSelectedProject();
  const [start, end] = selectedProject?.planning_horizon ?? ["", ""];

  const [openDialog, setOpenDialog] = useState<boolean>(false);
  const [startDate, setStartDate] = useState<string>(start);
  const [endDate, setEndDate] = useState<string>(end);
  const [edit, setEdit] = useState<boolean>(false);

  const { shifts, setShifts } = useShifts();
  const { generateShifts } = useGenerateShifts();
  const { shiftTypes } = useShiftTypes();




  useEffect(() => {

    setStartDate(start);
    setEndDate(end);

  }, [selectedProject])

  if(!selectedProject) return;


  const handleAdjustShifts = async (project: Project, old_horizon: any) => {

    const old_dates = generateDatesFromPlanningHorizon(old_horizon);
    const dates = generateDatesFromPlanningHorizon(project.planning_horizon);

    const [newDays, removedDays] = calculateStringDifference(dates, old_dates);    

    const removableShifts = shifts.filter((shift) => removedDays.includes(shift.start_time.split("T")[0]))
    const newShifts = generateShifts(newDays, shiftTypes);

    try {


      const res = await deleteShifts(removableShifts.map((shift) => shift.id), project.id);
      const res_ = await createShifts(newShifts, project.id)

      const updatedShifts = await getAllShifts(project.id);
      setShifts(updatedShifts);

    } catch (err: any) {
      throw new Error(err ?? "Failed to delete/create shifts");
    }

  }


  const handleUpdatePlanningHorizon = async () => {
    
    if (startDate && endDate &&  endDate.length == startDate.length && endDate < startDate) {
      alert("End date cannot be before start date");
      setStartDate(start);
      setEndDate(end);
      return;
    }

    if (formatDate(startDate, "weekday") !== "Mo" || formatDate(endDate, "weekday") !== "So"){
      alert("Start date has to be a monday and end date a sunday");
      setStartDate(start);
      setEndDate(end);
      return;
    }

    try {

      const old_horizon = selectedProject.planning_horizon;
      const editedProject: Project = {...selectedProject, planning_horizon: [startDate, endDate]}
      const res = await editProject(editedProject);

      if(!res.id) {
        alert("Failed to update planning horizon");
        return;
      }

      setSelectedProject(res);

      handleAdjustShifts(res, old_horizon);



    } catch (err: any) {
      alert(err ?? "An error occured when handling the editing project");
    }


  }



  return (

    <Dialog open={openDialog} onOpenChange={setOpenDialog}>
      <DialogTrigger asChild>

        <Button className="bg-gray-50 rounded-none border-border" variant={"outline"}>
          Manage Planning Horizon
        </Button>

      </DialogTrigger>
      <DialogContent className="!w-[48vw] !max-w-[1200px] h-[calc(80vh)]">
        <DialogHeader className="h-min">
          <DialogTitle> Manage Planning Horizon </DialogTitle>

        </DialogHeader>

        <div className="overflow auto h-150">

          <div className="flex gap-4 p-3 bg-gray-100 rounded-2xl">
            <div className="bg-white rounded-xl p-2 flex-1">

              <p className="font-semibold text-xl pb-2"> Current timespan:  </p> 
              <div className="flex flex-col gap-2 pl-10">

                <div className="flex gap-6 items-center">
                  <p> Start: </p>
                  <p className="text-2xl "> {formatDate(start, "weekday")}. {formatDate(start, "date")} </p>
                </div>

                <div className="flex gap-6 items-center">
                  <p> End: </p>
                  <p className="text-2xl"> {formatDate(end, "weekday")}. {formatDate(end, "date")} </p>
                </div>
              </div>

            </div>

            
            {!edit && (
              <div className="bg-white rounded-xl p-5 flex flex-col items-center justify-center">
                <Button 
                  className="rounded-none border-border" 
                  variant={"outline"}
                  onClick={() => setEdit(true)}
                >
                  Adjust timespan
                </Button>
              </div>
            )}


            {edit && (

            <div className="bg-white rounded-xl p-3 flex flex-col items-center justify-center">
      
              <div className="flex gap-2 items-center mb-2">
                <p className="w-10"> Start: </p>      
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="border border-border p-2 rounded"
                  />
              </div>

              <div className="flex gap-2 items-center">
                <p className="w-10"> End: </p>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  min={startDate}
                  className="border p-2 border-border rounded"
                  />
              </div>

              <div className="flex gap-2 mt-2 justify-end w-full">
                <Button 
                  className="rounded-none border-border h-6" 
                  variant={"outline"}
                  onClick={() => setEdit(false)}
                  >
                  Cancel
                </Button>

                <Button 
                  className="rounded-none border-border h-6" 
                  variant={"outline"}
                  onClick={() => {handleUpdatePlanningHorizon(); setEdit(false)}}
                  >
                  Save
                </Button>
              </div>

            </div>

            )}
          </div>
          

          <div className="mt-4 p-3 bg-gray-100 rounded-2xl">

            <div className="bg-white rounded-xl p-5 flex flex-col">

              <p className="font-semibold">
                Note:
              </p>

              <div className="flex items-center justify-center mt-2">
                <p className="italic text-muted-foreground">
                  Changing the planning horizon will result in the deletion/creation of shifts. Undoing this step is not possible.
                </p>
              </div>

            </div>

          </div>


        </div>

      </DialogContent>
    </Dialog>

  )
}