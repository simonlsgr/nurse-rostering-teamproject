"use client";

import { useEffect, useState } from "react";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "../ui/dialog";
import { Nurse, Shift } from "@/types/nurseVars";
import { useDetailViewNurse, useEditAttributes, useNurses, useOpenNurseDetailView } from "@/store/nurseStore";
import DynamicShiftList from "../rostering/DynamicShiftList";
import { useInstance } from "@/store/instanceStore";
import { capitalize, Tooltip } from "@mui/material";
import { createDefaultNurse, formatDate } from "@/lib/utils";
import { Pencil } from 'lucide-react';
import CalendarPicker from "./DetailViewEditDaysOffCalendar";
import { CalendarMinus2 } from 'lucide-react';
import { motion, AnimatePresence } from "framer-motion";
import { Check } from 'lucide-react';
import { X } from 'lucide-react';
import { Button } from "../ui/button";
import DeleteNurseDialog from "./DeleteNurseDialog";
import { editNurse } from "@/app/api/nurse";
import { useSelectedProject } from "@/store/projectStore";
import DetailViewAddDaysCalendar from "./DetailViewEditDaysOffCalendar";
import DetailViewEditDaysOffCalendar from "./DetailViewEditDaysOffCalendar";

export default function NurseDetailView() {

  const { updateNurse } = useNurses();
  const { shifts } = useInstance();
  const { detailViewNurse, setDetailViewNurse } = useDetailViewNurse();
  const { openNurseDetailView, setOpenNurseDetailView } = useOpenNurseDetailView();
  const [ editedNurse, setEditedNurse ] = useState<Nurse>(createDefaultNurse());
  const { selectedProject } = useSelectedProject();

  
  const { editAttributes, setEditAttribute, setEditAttributes } = useEditAttributes();
  

  useEffect(() => {
    if (detailViewNurse) {
      setEditedNurse(detailViewNurse);
    }
  }, [detailViewNurse]);


  if(!detailViewNurse) return;


  const displayMaximumShiftsPerType = () => {

    return (
      <div className="pb-1">
        {Object.keys(detailViewNurse.maximum_number_of_shifts_per_type).map((key) => {
          return (
            <p key={key}> {key}: {detailViewNurse.maximum_number_of_shifts_per_type[key]} </p>
          )
        })}
      </div>
    )
  }

  const setPreferredShiftWeight = (weight: number, shift: Shift) => {

    setDetailViewNurse(prev => ({
      ...prev,
      preferred_shift_weight: {
        ...detailViewNurse.preferred_shift_weight,
        [shift.uid]: weight
      }
    }));
  }

  const setPreferredOffShiftWeight = (weight: number, shift: Shift) => {

    setDetailViewNurse(prev => ({
      ...prev,
      preferred_off_shift_weight: {
        ...detailViewNurse.preferred_off_shift_weight,
        [shift.uid]: weight
      }
    }));
  }

  const setDaysOff = (dates: Date[]) => {

    const string_dates = dates.map((date) => date.toISOString());
    const updatedNurse = { ...editedNurse, days_off: string_dates };
    setEditedNurse(updatedNurse);
    handleUpdateNurse("days_off", updatedNurse);
  }




  const dynamicAttributeDisplay = (key: string) => {
    
    // these attributes are not needed currently
/*     if (key == "staff") {
      return (
        <div className="flex gap-2 items-center">
          <Switch
            checked={editedNurse.staff}
            onChange={(event, newChecked) => {
              setEditedNurse({...editedNurse, "staff": !editedNurse.staff});
            }}
            />
          <p> {editedNurse.staff ? "true" : "false"} </p>
        </div>

      )
    }

    if (key == "min_time_between_shifts") {
      return (
        <Textarea
          className="mb-2 min-h-none"     
          value={editedNurse[key]}
          onChange={(e) => {
            setEditedNurse({...editedNurse, [key]: e.target.value})
          }}     
        />
      )
    } */

    if (key == "maximum_number_of_shifts_per_type") {
      return (
        <div className="pb-1">

          {Object.keys(editedNurse[key]).map((type) => (

            <div 
              key={type}
              className="flex gap-1 items-center"
            >
              <p className="mb-2"> {type}: </p>
              <input
                className="border border-border rounded-md p-1 mb-2"
                type="text"
                inputMode="numeric"
                value={editedNurse[key][type]}
                onChange={(e) => {
                  const val = Number(e.target.value.replace(/\D/g, ""));
                  setEditedNurse(prev => ({
                    ...prev,
                    [key]: {
                      ...(prev[key as keyof Nurse] as Record<string, number>),
                      [type]: val
                    }
                  }));
                  setDetailViewNurse(prev => ({
                    ...prev,
                    [key]: {
                      ...(prev[key as keyof Nurse] as Record<string, number>),
                      [type]: val
                    }
                  }));
                }}
              />
            </div>

          ))}
      
      </div>
      )
    }

    return (
      <input
        className="border border-border rounded-md p-1 mb-2"
        type="text"
        inputMode="numeric"
        value={editedNurse[key as keyof Nurse] as any}
        onChange={(e) => {
          const val = Number(e.target.value.replace(/\D/g, ""));
          setEditedNurse({...editedNurse, [key]: val});
        }}
      />
    )
  }


  // have the edited Nurse as parameter, if state is not updated fast enough
  const handleUpdateNurse = async (key?: keyof Nurse, nurse?: Nurse) => {

    if (!selectedProject) return;

    try {
      const adjustedNurse = key ? {...detailViewNurse, [key]: nurse ? nurse[key] : editedNurse[key]} : nurse ? nurse : editedNurse;

      const res = await editNurse(adjustedNurse, selectedProject.id);
      updateNurse(adjustedNurse);
      setEditAttributes({});
      setDetailViewNurse(adjustedNurse);  

    } catch (err: any) {
      alert(err ?? "Failed to edit nurse");
    }

  }


  return (


    <Dialog open={openNurseDetailView} onOpenChange={setOpenNurseDetailView}>

      <DialogContent className="!w-[48vw] !max-w-none h-[calc(80vh)]">
        <DialogHeader>
          <DialogTitle>
            
            {!editAttributes["name"] && (

              <div className="flex gap-2 group">
                Nurse {detailViewNurse.name}
                <Pencil 
                  fontSize={"small"} 
                  className="p-1 opacity-0 group-hover:opacity-100 transition-all duration-170 ease-in-out hover:bg-gray-100 rounded-lg"
                  onClick={() => setEditAttribute("name", true)}
                />
                
              </div>
            )}


            {editAttributes["name"] && (
            
            
            <AnimatePresence mode="popLayout">
              <motion.div
                layout
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.17 }}
                className="select-none"
              >
              
            
                <div className="flex gap-2 items-center">
                  Nurse
                  <input
                    className="border border-border rounded-md p-1"
                    type="text"
                    inputMode="numeric"
                    value={editedNurse["name"]}
                    onChange={(e) => {
                      const val = e.target.value;
                      setEditedNurse(prev => ({
                        ...prev,
                        "name": val
                      }));
                    }}
                  />


                  <Tooltip
                    title="Save"
                    enterDelay={100}
                    enterNextDelay={100}
                  >
                    <Check 
                      fontSize={"small"}
                      className="transition-all duration-170 ease-in-out hover:bg-gray-100 rounded-lg"
                      onClick={() => { handleUpdateNurse("name"); setEditAttribute("name", false); }}
                    />
                  </Tooltip>
            
                  <Tooltip
                    title="Cancel"
                    enterDelay={100}
                    enterNextDelay={100}
                  >
                  <X
                    fontSize={"small"} 
                    className="transition-all duration-170 ease-in-out hover:bg-gray-100 rounded-lg"
                    onClick={() => setEditAttribute("name", false)}
                  />
                  </Tooltip>
            
                </div>
              </motion.div>
            </AnimatePresence>
            
            )}
                      
            </DialogTitle>
        </DialogHeader>

        <div className="overflow-auto">
        <div className="flex gap-4">
          <div key={"preferred_shifts"} className={`mb-2 overflow-auto max-h-[calc(40vh)] ${detailViewNurse.preferred_shifts.length >= 1 ?"h-[calc(40vh)]" : "h-min"} w-[calc(20vw)] max-w-100 border border-border rounded-3xl p-2 pr-0 bg-gray-50 shadow-xs`}>

            <h2 className="pb-2 pl-2 font-semibold"> Preferred Shifts: </h2>
            <DynamicShiftList 
              shifts={shifts.filter((s) => detailViewNurse.preferred_shifts.includes(s.uid))} 
              shift_weights={detailViewNurse.preferred_shift_weight} 
              setShiftWeight={setPreferredShiftWeight}
              selectable={false}  

            />

          </div>

          <div key={"preferred_off_shifts"} className={`mb-2 overflow-auto max-h-[calc(40vh)] ${detailViewNurse.preferred_off_shifts.length >= 1 ?"h-[calc(40vh)]" : "h-min"} w-[calc(20vw)] max-w-100 border border-border rounded-3xl p-2 pr-0 bg-gray-50 shadow-xs`}>

            <h2 className="pb-2 pl-2 font-semibold"> Preferred Off-Shifts: </h2>
            <DynamicShiftList 
              shifts={shifts.filter((s) => detailViewNurse.preferred_off_shifts.includes(s.uid))} 
              shift_weights={detailViewNurse.preferred_off_shift_weight}
              setShiftWeight={setPreferredOffShiftWeight}
              />

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
                      title="Edit Off-Days"
                      enterDelay={100}
                      enterNextDelay={100}
                    >

                    <div>
                      <DetailViewEditDaysOffCalendar selectedDates={detailViewNurse.days_off.map((date) => new Date(date))} setSelectedDates={setDaysOff} />
                    </div>
                    </Tooltip>
                    
                    <Tooltip
                      title="Close Menu"
                      enterDelay={100}
                      enterNextDelay={100}
                    >
                    <X
                      fontSize={"small"} 
                      className="transition-all duration-170 ease-in-out hover:bg-gray-100 rounded-lg"
                      onClick={() => setEditAttribute("days_off", false)}
                    />
                    </Tooltip>

                  </div>
                </motion.div>
              </AnimatePresence>

            )}

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

        {Object.keys(detailViewNurse)
        .filter((keyy) => !["id", "db_id", "uid", "name", "preferred_shifts", "preferred_off_shifts", "blocked_shifts", "preferred_shift_weight", "days_off", "preferred_off_shift_weight", "min_time_between_shifts", "staff"].includes(keyy))
        .map((key) => 
          <div key={key} className="mb-2">

            <div className="flex gap-3 group"> 
              <p className="font-semibold mb-2" key={`title-${key}`}>
                {capitalize(key.replaceAll("_", " "))}:
              </p>

              {!editAttributes[key] && (
                <Pencil 
                  fontSize={"small"} 
                  className="p-1 opacity-0 group-hover:opacity-100 transition-all duration-170 ease-in-out hover:bg-gray-100 rounded-lg"
                  onClick={() => { setEditAttribute(key, true); }}  
                />
              )}

              {editAttributes[key] && (


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
                        title="Save"
                        enterDelay={100}
                        enterNextDelay={100}
                      >
                        <Check 
                          fontSize={"small"}
                          className="transition-all duration-170 ease-in-out hover:bg-gray-100 rounded-lg"
                          onClick={() => { handleUpdateNurse(key as keyof Nurse); setEditAttribute(key, false); }}
                        />
                      </Tooltip>

                      <Tooltip
                        title="Cancel"
                        enterDelay={100}
                        enterNextDelay={100}
                      >
                      <X
                        fontSize={"small"} 
                        className="transition-all duration-170 ease-in-out hover:bg-gray-100 rounded-lg"
                        onClick={() => setEditAttribute(key, false)}
                      />
                      </Tooltip>

                    </div>
                  </motion.div>
                </AnimatePresence>

              )}

              
            </div>

            <div className={`border-b border-border w-full pl-1 overflow-auto`} key={`content-${key}`}>

              {!editAttributes[key] && (
                <div>
                  {key == "maximum_number_of_shifts_per_type" ? displayMaximumShiftsPerType() : JSON.stringify(detailViewNurse[key as keyof Nurse])}
                </div>
              )}

              {editAttributes[key] && (
                <div>

                  {dynamicAttributeDisplay(key)}

                </div>
              )}


            </div>  
          </div>
        )}

          <div className="flex justify-end mt-4 mr-4">
            <DeleteNurseDialog />
          </div>


        </div>
        


        <DialogFooter className="mt-4 flex items-end">
        </DialogFooter>
      </DialogContent>
    </Dialog>

  )
}