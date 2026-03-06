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



export default function NurseDetailView() {

  const { shifts } = useInstance();
  const { detailViewNurse, setDetailViewNurse } = useDetailViewNurse();
  const { openNurseDetailView, setOpenNurseDetailView } = useOpenNurseDetailView();
  
  if(!detailViewNurse) return;

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
            <DynamicShiftList shifts={shifts.filter((s) => detailViewNurse.preferred_shifts.includes(s.uid))} />

          </div>

          <div key={"preferred_off_shifts"} className={`mb-2 overflow-auto max-h-[calc(40vh)] ${detailViewNurse.preferred_off_shifts.length >= 1 ?"h-[calc(40vh)]" : "h-min"} w-[calc(15vw)] max-w-100 border border-border rounded-3xl p-2 pr-0 bg-gray-50 shadow-xs`}>

            <h2 className="pb-2 pl-2 font-semibold"> Preferred Off-Shifts: </h2>
            <DynamicShiftList shifts={shifts.filter((s) => detailViewNurse.preferred_off_shifts.includes(s.uid))} />

          </div>

          <div key={"blocked_shifts"} className={`mb-2 overflow-auto max-h-[calc(40vh)] ${detailViewNurse.blocked_shifts.length >= 1 ?"h-[calc(40vh)]" : "h-min"} w-[calc(15vw)] max-w-100 border border-border rounded-3xl p-2 pr-0 bg-gray-50 shadow-xs`}>

            <h2 className="pb-2 pl-2 font-semibold"> Blocked Shifts: </h2>
            <DynamicShiftList shifts={shifts.filter((s) => detailViewNurse.blocked_shifts.includes(s.uid))} />

          </div>

        </div>

        {/* this is just temporary, need better visualizations for all attributes */}
        {Object.keys(detailViewNurse)
        .filter((keyy) => !["db_id", "uid", "name", "preferred_shifts", "preferred_off_shifts", "blocked_shifts", "preferred_shift_weight"].includes(keyy))
        .map((key) => 
          <div key={key} className="mb-2">

            <p className="font-semibold mb-2" key={`title-${key}`}>
              {capitalize(key.replaceAll("_", " "))}:
            </p>

            <p className={`border-b border-border w-full pl-1 overflow-auto text-sm`} key={`content-${key}`}>
              {JSON.stringify(detailViewNurse[key as keyof Nurse])}
            </p>  
          </div>
        )}
        </div>


        <DialogFooter className="mt-4 flex items-end">
        
        <Button 
          className="w-20"
        >
          Edit
        </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

  )
}