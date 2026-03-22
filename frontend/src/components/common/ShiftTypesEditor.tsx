import { useEffect, useState } from "react";
import { Trash2 } from "lucide-react";
import { ShiftType } from "@/types/projectVars";
import { useNewProject } from "@/store/projectStore";
import { Tooltip } from "@mui/material";
import { motion, AnimatePresence } from "framer-motion";
import DeleteShiftTypeDialog from "./DeleteShiftTypeDialog";
import { EditShiftTypeDialog } from "./EditShiftTypeDialog";


type ShiftTypesEditorProps = {

  actualShiftTypes: ShiftType[];
  setActualShiftTypes: any;
}


export default function ShiftTypesEditor({ actualShiftTypes, setActualShiftTypes }: ShiftTypesEditorProps){

  const [shiftTypes, setShiftTypes] = useState<ShiftType[]>(actualShiftTypes);
  const [newShift, setNewShift] = useState({
    name: "",
    duration: "00:00:00", 
  });
  
  const isValid =
  newShift.name.trim() !== "" &&
  newShift.duration !== "" &&
  newShift.duration !== "00:00:00" && 
  !shiftTypes.some((s) => s.name.toLowerCase() == newShift.name.trim().toLowerCase());


  useEffect(() => {

    setShiftTypes(actualShiftTypes);

  }, [actualShiftTypes])


  useEffect(() => {

    setActualShiftTypes(shiftTypes);

  }, [shiftTypes])


  const setShiftType = (editedShift: ShiftType) => {

    const other_shifts = shiftTypes.filter((shiftType) => shiftType.id !== editedShift.id);
    setShiftTypes([editedShift, ...other_shifts]);
  }


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

  const deleteShift = (id: string) => {
    setShiftTypes(prev => prev.filter(shift => shift.id !== id));
  };


  return (
    <div className="h-full">
      <p className="font-semibold mb-3"> Add Shift Types: </p>
      <div className="flex gap-2 items-end">
        
        <input
          type="text"
          placeholder="Shift Name"
          value={newShift.name}
          onChange={(e) =>
            setNewShift(prev => ({ ...prev, name: e.target.value }))
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
            value={newShift.duration}
            onChange={(e) =>
              setNewShift(prev => ({ ...prev, duration: e.target.value }))
            }
            className="border border-border p-2 rounded"
          />
        </Tooltip>
        
        <button
          className={`px-3 py-2 rounded ${
            isValid ? "bg-blue-500 text-white" : "bg-gray-300 cursor-not-allowed"
          }`}
          disabled={!isValid}
          onClick={() => {
            const start = "00:00:00";
            const end = calculateEndTime(newShift.duration);
          
            setShiftTypes(prev => [
              ...prev,
              {
                id: crypto.randomUUID(),
                name: newShift.name,
                duration: newShift.duration,
                start,
                end,
                not_followed_by_shift_types: []
              }
            ]);
          
            setNewShift({ name: "", duration: "00:00:00" });
          }}
        >
        Add
        </button>
        
      </div>

      <div className="pt-3 pb-1 text-sm text-muted-foreground"> Current shift types: </div>

      <div className="flex flex-col gap-2 overflow-auto h-60">
        {shiftTypes.map((shift) => (


        <AnimatePresence mode="popLayout" key={shift.id}>
          <motion.div
            layout
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.17 }}
            className="select-none"
          >


          <div
            key={shift.id}
            className="border border-border p-2 rounded-xl flex justify-between items-center"
          >


            <div>
              <p className="font-semibold">{shift.name}</p>
              <p className="text-sm text-gray-600">
                Duration: {shift.duration} h
              </p>
            </div>
        
            <div className="flex gap-3 items-center">
              <EditShiftTypeDialog shiftType={shift} />
              <DeleteShiftTypeDialog shiftType={shift} deleteShiftType={deleteShift} />
            </div>

          </div>
        </motion.div>
      </AnimatePresence>
      ))}
            

      </div>

    </div>
  )
}


