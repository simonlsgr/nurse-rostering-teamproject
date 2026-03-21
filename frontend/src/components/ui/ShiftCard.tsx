import { formatDate } from "@/lib/utils";
import { Shift } from "@/types/nurseVars";
import { Pencil, ScanSearch } from 'lucide-react';
import { Tooltip } from "@mui/material";
import { motion, AnimatePresence } from "framer-motion";
import { Check } from 'lucide-react';
import { X } from 'lucide-react';

import { useState } from "react";
import { useShifts } from "@/store/nurseStore";
import { editShift } from "@/app/api/shift";
import { useSelectedProject } from "@/store/projectStore";

type ShiftCardProps = {
  shift: Shift;
  weight?: number;
  setWeight?: any;
  selectable?: boolean;
  selected?: boolean;
  editDemand?: boolean;
};


export default function ShiftCard({ shift, weight, setWeight, selectable = false, selected = false, editDemand = false }: ShiftCardProps){

  const [editWeight, setEditWeight] = useState<boolean>(false);
  const [newWeight, setNewWeight] = useState<number>(weight ?? 1);
  const [editDemands, setEditDemands] = useState<boolean>(false);

  const [demand, setDemand] = useState<number>(shift.demand);
  const [weightBelowDemand, setWeightBelowDemand] = useState<number>(shift.weight_below_demand);
  const [weightAboveDemand, setWeightAboveDemand] = useState<number>(shift.weight_above_demand);

  const { updateShift } = useShifts();
  const { selectedProject } = useSelectedProject();

  const handleUpdateShift = () => {

    if(!selectedProject) return;

    try {

      const editedShift = {...shift, demand: demand, weight_below_demand: weightBelowDemand, weight_above_demand: weightAboveDemand}; 
      
      editShift(editedShift, selectedProject.id)
      updateShift(editedShift);
    } catch (err: any) {
      alert(err ?? "Failed to edit shift");
    }

  }

  if (weight && !setWeight) return;

  return (
    
    <div 
      className={`border group border-gray-400 rounded-lg w-[calc(100%-1rem)] h-auto p-2 mb-2 ml-2 mt-2 shadow transition-all duration-170 ease-in-out flex items-center ${selectable && "hover:bg-orange-100"} ${selected && selectable ? "bg-red-200 hover:bg-red-100" : ""} bg-orange-200`}
    >
      <div className="flex-1 overflow-auto">
        <div className="">
          <p className="truncate font-semibold"> Shift {shift.name} </p>              
          <p> {formatDate(shift.start_time, "weekday")}. {formatDate(shift.start_time, "date")}</p>
          
          {!editDemands && (
            <div>
              <p> Demand: {shift.demand}  </p>
              <p> W. below demand: {shift.weight_below_demand} </p>
              <p> W. above demand: {shift.weight_above_demand} </p>
            </div>
          )}

          {editDemands && (
            <div>

            <div className="flex gap-2 items-center">
              <p> Demand: </p>
              <input
                className="border rounded-md p-1 w-10"
                type="text"
                inputMode="numeric"
                value={demand}
                onChange={(e) => {
                  const val = Number(e.target.value.replace(/\D/g, ""));
                  setDemand(val);
                }}
                />
            </div>

            <div className="flex gap-2 items-center">
              <p> W. below demand: </p>
              <input
                className="border rounded-md p-1 w-10"
                type="text"
                inputMode="numeric"
                value={weightBelowDemand}
                onChange={(e) => {
                  const val = Number(e.target.value.replace(/\D/g, ""));
                  setWeightBelowDemand(val);
                }}
                />
            </div>

            <div className="flex gap-2 items-center">
              <p> W. above demand: </p>
              <input
                className="border rounded-md p-1 w-10 m-1"
                type="text"
                inputMode="numeric"
                value={weightAboveDemand}
                onChange={(e) => {
                  const val = Number(e.target.value.replace(/\D/g, ""));
                  setWeightAboveDemand(val);
                }}
                />
            </div>

          </div>
          )}



        </div>
        {/* <p> Time: {formatDate(shift.start_time, "time")} - {formatDate(shift.end_time, "time")}</p>  */}
        
        {weight != undefined && (
          <div className="group" onClick={(e) => e.stopPropagation()}>
            {!editWeight && (
              <div className="flex gap-2">
                <p> Weight: {weight} </p>
                {setWeight && (
                  <Pencil 
                  fontSize={"small"} 
                  className="p-1 opacity-0 group-hover:opacity-100 transition-all duration-170 ease-in-out hover:bg-orange-100 rounded-lg"
                  onClick={() => { setEditWeight(true); }}  
                  />
                )}
              </div>
            )}
            {editWeight && (
              <div className="flex gap-2 items-center">
                <p> Weight: </p>
                <input
                className="border rounded-md p-1 w-10"
                type="text"
                inputMode="numeric"
                value={newWeight}
                onChange={(e) => {
                  const val = Number(e.target.value.replace(/\D/g, ""));
                  setNewWeight(val);
                }}
                />
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
                          onClick={() => { setWeight(newWeight, shift); setEditWeight(false);}}
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
                        onClick={() => { setNewWeight(weight); setEditWeight(false); }}
                      />
                      </Tooltip>

                    </div>
                  </motion.div>
                </AnimatePresence>
              </div>
            )}
          </div>
        )}
      </div>

      {!selectable && editDemand && (
        <div>

          {!editDemands && (            
            <Pencil
              className="opacity-0 group-hover:opacity-100 transition hover:bg-gray-200 rounded p-1     rounded-md"
              fontSize={"small"}
              onClick={() => setEditDemands(true)}
            />
          )}

          {editDemands && (
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
                      onClick={() => { handleUpdateShift(); setEditDemands(false);}}
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
                      onClick={() => { setEditDemands(false); }}
                    />
                  </Tooltip>
                </div>
              </motion.div>
            </AnimatePresence>
          )}


        </div>
      )}  
    </div>
  );


}