import { useState } from "react";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "../ui/dialog";
import { Button } from "../ui/button";
import AddIcon from '@mui/icons-material/Add';
import { Input } from "../ui/input";
import { Nurse } from "@/types/nurseVars";
import { useDetailViewNurse, useOpenNurseDetailView } from "@/store/nurseStore";
import DynamicShiftList from "../rostering/DynamicShiftList";
import { useInstance } from "@/store/instanceStore";
import { capitalize } from "@mui/material";
import { formatDate } from "@/lib/utils";



export default function NurseDetailView() {

  const { shifts } = useInstance();
  const { detailViewNurse, setDetailViewNurse } = useDetailViewNurse();
  const { openNurseDetailView, setOpenNurseDetailView } = useOpenNurseDetailView();
  


  if(!detailViewNurse) return;


  const displayMaximumShiftsPerType = () => {

    return (
      <div className="pb-1">
        <p> Early: {detailViewNurse.maximum_number_of_shifts_per_type["E"]} </p>
        <p> Late: {detailViewNurse.maximum_number_of_shifts_per_type["L"]} </p>
        </div>
    )
  }


  return (


    <Dialog open={openNurseDetailView} onOpenChange={setOpenNurseDetailView}>

      <DialogContent className="!w-[55vw] !max-w-none h-[calc(80vh)]">
        <DialogHeader>
          <DialogTitle>Nurse {detailViewNurse.name}</DialogTitle>
        </DialogHeader>

        <div className="overflow-auto">
        <div className="flex gap-4">
          <div key={"preferred_shifts"} className={`mb-2 overflow-auto max-h-[calc(40vh)] ${detailViewNurse.preferred_shifts.length >= 1 ?"h-[calc(40vh)]" : "h-min"} w-[calc(15vw)] max-w-100 border border-border rounded-3xl p-2 pr-0 bg-gray-50 shadow-xs`}>

            <h2 className="pb-2 pl-2 font-semibold"> Preferred Shifts: </h2>
            <DynamicShiftList shifts={shifts.filter((s) => detailViewNurse.preferred_shifts.includes(s.uid))} shift_weights={detailViewNurse.preferred_shift_weight}/>

          </div>

          <div key={"preferred_off_shifts"} className={`mb-2 overflow-auto max-h-[calc(40vh)] ${detailViewNurse.preferred_off_shifts.length >= 1 ?"h-[calc(40vh)]" : "h-min"} w-[calc(15vw)] max-w-100 border border-border rounded-3xl p-2 pr-0 bg-gray-50 shadow-xs`}>

            <h2 className="pb-2 pl-2 font-semibold"> Preferred Off-Shifts: </h2>
            <DynamicShiftList shifts={shifts.filter((s) => detailViewNurse.preferred_off_shifts.includes(s.uid))} shift_weights={detailViewNurse.preferred_off_shift_weight}/>

          </div>

          <div key={"blocked_shifts"} className={`mb-2 overflow-auto max-h-[calc(40vh)] ${detailViewNurse.blocked_shifts.length >= 1 ?"h-[calc(40vh)]" : "h-min"} w-[calc(15vw)] max-w-100 border border-border rounded-3xl p-2 pr-0 bg-gray-50 shadow-xs`}>

            <h2 className="pb-2 pl-2 font-semibold"> Blocked Shifts: </h2>
            <DynamicShiftList shifts={shifts.filter((s) => detailViewNurse.blocked_shifts.includes(s.uid))} />

          </div>

        </div>

        <div className="mb-2">

          <p className="font-semibold mb-2">
            Days off:
          </p>

          <div className={`border-b border-border w-full pl-1 overflow-auto`}>
            {detailViewNurse.days_off.map((day) => (


              <div key={day} className="p-1">

                {"- " + formatDate(day, "weekday") + ". " + formatDate(day, "date")}

              </div>

            ))}
          </div>  
        </div>

        {/* this is just temporary, need better visualizations for all attributes */}
        {Object.keys(detailViewNurse)
        .filter((keyy) => !["db_id", "uid", "name", "preferred_shifts", "preferred_off_shifts", "blocked_shifts", "preferred_shift_weight", "days_off"].includes(keyy))
        .map((key) => 
          <div key={key} className="mb-2">

            <p className="font-semibold mb-2" key={`title-${key}`}>
              {capitalize(key.replaceAll("_", " "))}:
            </p>

            <div className={`border-b border-border w-full pl-1 overflow-auto`} key={`content-${key}`}>
              {key == "maximum_number_of_shifts_per_type" ? displayMaximumShiftsPerType() : JSON.stringify(detailViewNurse[key as keyof Nurse])}
            </div>  
          </div>
        )}
        </div>


        <DialogFooter className="mt-4 flex items-end">
        
        </DialogFooter>
      </DialogContent>
    </Dialog>

  )
}