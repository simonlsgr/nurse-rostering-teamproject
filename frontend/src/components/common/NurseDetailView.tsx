"use client";

import { useEffect, useState } from "react";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "../ui/dialog";
import { Button } from "../ui/button";
import AddIcon from '@mui/icons-material/Add';
import { Input } from "../ui/input";
import { Nurse } from "@/types/nurseVars";
import { useDetailViewNurse, useEditAttributes, useOpenNurseDetailView } from "@/store/nurseStore";
import DynamicShiftList from "../rostering/DynamicShiftList";
import { useInstance } from "@/store/instanceStore";
import { capitalize, Tooltip } from "@mui/material";
import { formatDate } from "@/lib/utils";
import { Pencil } from 'lucide-react';
import { Calendar } from "@/components/ui/calendar";
import CalendarPicker from "./DetailViewAddDaysCalendar";
import { CalendarPlus2 } from 'lucide-react';
import { CalendarMinus2 } from 'lucide-react';
import { Undo2 } from 'lucide-react';
import { motion, AnimatePresence } from "framer-motion";

export default function NurseDetailView() {

  const { shifts } = useInstance();
  const { detailViewNurse, setDetailViewNurse } = useDetailViewNurse();
  const { openNurseDetailView, setOpenNurseDetailView } = useOpenNurseDetailView();

  const { editAttributes, setEditAttribute, setEditAttributes } = useEditAttributes();

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

        <div className="mb-2 mt-4">

          <div className="flex gap-3 group">
            <p className="font-semibold mb-2">
              Days off:
            </p>

            {!editAttributes["days_off"] && (
              <Pencil 
                fontSize={"small"} 
                className="p-1 opacity-0 group-hover:opacity-100 transition-all duration-170 ease-in-out hover:bg-gray-100 rounded-lg"
                onClick={() => setEditAttribute("days_off", true)}
              />
            )}


            {editAttributes["days_off"] && (


              <AnimatePresence mode="popLayout">
                <motion.div
                  layout
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ duration: 0.17 }}
                  className="select-none"
                >


                  <div className="flex gap-2">
                    <Tooltip
                      title="Add Off-Days"
                      enterDelay={100}
                      enterNextDelay={100}
                    >
                      <CalendarPicker />
                    </Tooltip>
                    
                    <Tooltip
                      title="Remove Off-Days"
                      enterDelay={100}
                      enterNextDelay={100}
                    >
                    <CalendarMinus2
                      fontSize={"small"} 
                      className="transition-all duration-170 ease-in-out hover:bg-gray-100 rounded-lg"
                    />
                    </Tooltip>

                    <Tooltip
                      title="Close Menu"
                      enterDelay={100}
                      enterNextDelay={100}
                    >
                    <Undo2
                      fontSize={"small"} 
                      className="transition-all duration-170 ease-in-out hover:bg-gray-100 rounded-lg"
                      onClick={() => setEditAttribute("days_off", false)}
                    />
                    </Tooltip>

                  </div>
                </motion.div>
              </AnimatePresence>

            )}


            {/* <CalendarPicker /> */}

          </div>

          <div className={`border-b border-border w-full pl-1 overflow-auto`}>
            {detailViewNurse.days_off.map((day) => (

              <div key={day}>
                
                <div className="p-1">
                
                  {"- " + formatDate(day, "weekday") + ". " + formatDate(day, "date")}
                
                </div>

              </div>
            ))}
          </div>  
        </div>

        {/* this is just temporary, need better visualizations for all attributes */}
        {Object.keys(detailViewNurse)
        .filter((keyy) => !["db_id", "uid", "name", "preferred_shifts", "preferred_off_shifts", "blocked_shifts", "preferred_shift_weight", "days_off", "preferred_off_shift_weight"].includes(keyy))
        .map((key) => 
          <div key={key} className="mb-2">

            <div className="flex gap-3 group"> 
              <p className="font-semibold mb-2" key={`title-${key}`}>
                {capitalize(key.replaceAll("_", " "))}:
              </p>

              <Pencil fontSize={"small"} className="p-1 opacity-0 group-hover:opacity-100 transition-all duration-170 ease-in-out hover:bg-gray-100 rounded-lg"/>
            </div>

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