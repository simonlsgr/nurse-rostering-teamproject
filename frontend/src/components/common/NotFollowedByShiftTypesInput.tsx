import { useNewProject } from "@/store/projectStore";
import { ShiftType } from "@/types/projectVars";
import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Trash2 } from "lucide-react";
import { Dot } from 'lucide-react';

type Constraint = {
  beforeId: string; 
  afterId: string;  
};


export default function NotFollowedByShiftTypesInput() {


  const { newProject, setNewProject } = useNewProject();

  const [shiftTypes, setShiftTypes] = useState<ShiftType[]>(newProject.shift_types ?? []);
  const [constraints, setConstraints] = useState<Constraint[]>([]);
  const [selectedLeft, setSelectedLeft] = useState<string>("");
  const [selectedRight, setSelectedRight] = useState<string>("");


  useEffect(() => {

    if(!newProject.shift_types) return;

    setShiftTypes(newProject.shift_types);

  }, [newProject.shift_types])

  useEffect(() => {

    updateShiftConstraints(constraints);

  }, [constraints]);



  const addConstraint = () => {
    if (!selectedLeft || !selectedRight) return;

    // avoid duplicate entries
    if (constraints.some(c => c.beforeId === selectedLeft && c.afterId === selectedRight)) {
      alert("Constraint already exists!");
      return;
    }

    setConstraints(prev => [
      ...prev,
      { beforeId: selectedLeft, afterId: selectedRight }
    ]);

    setSelectedLeft("");
    setSelectedRight("");
  };

  const removeConstraint = (index: number) => {
    setConstraints(prev => prev.filter((_, i) => i !== index));
  };


  const updateShiftConstraints = (constraints: Constraint[]) => {
    setNewProject(prev => {
      if (!prev.shift_types) return prev;
  
      const updatedShiftTypes = prev.shift_types.map(shift => {
        // constraints for this shift
        const forbidden = constraints
          .filter(c => c.beforeId === shift.id)
          .map(c => c.afterId);
  
        return {
          ...shift,
          not_followed_by_shift_types: forbidden
        };
      });
  
      return {
        ...prev,
        shift_types: updatedShiftTypes
      };
    });
  };


  return (
    <div>

    <p className="font-semibold mb-4"> Type not followed by type constraint: </p>
    <div className="">
    
      {!newProject.shift_types || newProject.shift_types.length <= 1 && (
        <p className="text-muted-foreground italic p-2"> Not enough shift types specified </p>
      )}


      {newProject.shift_types && newProject.shift_types.length > 1 && (
      <div className="flex flex-col gap-4">

      <div className="flex gap-2 items-center">

        <select
          value={selectedLeft}
          onChange={e => setSelectedLeft(e.target.value)}
          className="border border-border p-2 rounded"
        >
          <option value="">Select Shift Type</option>
          {shiftTypes.map(s => (
            <option key={s.id} value={s.id}>{s.name}</option>
          ))}
        </select>
        
        <span className="pl-4 pr-4 text-muted-foreground"> not followed by </span>
        
        <select
          value={selectedRight}
          onChange={e => setSelectedRight(e.target.value)}
          className="border border-border p-2 rounded"
        >
          <option value="">Select Shift Type</option>
          {shiftTypes.map(s => (
            <option key={s.id} value={s.id}>{s.name}</option>
          ))}
        </select>
        
        <button
          onClick={addConstraint}
          disabled={!selectedLeft || !selectedRight}
          className={`px-3 py-2 rounded ${
            !selectedLeft || !selectedRight ? "bg-gray-300 cursor-not-allowed" : "bg-blue-500 text-white"
          }`}
        >
          Add
        </button>
      </div>
        
      {/* Liste der Constraints */}
      <div className="flex flex-col gap-2">
        {constraints.map((c, index) => {
          const leftShift = shiftTypes.find(s => s.id === c.beforeId)?.name;
          const rightShift = shiftTypes.find(s => s.id === c.afterId)?.name;
        


          
          return (
            <AnimatePresence mode="popLayout" key={index}>
            <motion.div
              layout
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.17 }}
              className="select-none"
            >
  

            <div
              key={index}
              className="flex justify-between items-center border border-border p-2 rounded-xl"
            >

              <div className="flex items-center">
                <Dot className="mr-3"/>
                <span className="flex gap-3 items-center">
                  
                  <p className="font-semibold">
                    {leftShift}
                  </p>
                  
                  <p className="text-muted-foreground">is not followed by</p> 
                  
                  <p className="font-semibold">
                    {rightShift}
                  </p>
                </span>
              </div>
              <button
                onClick={() => removeConstraint(index)}
                className="text-red-500 hover:bg-red-100 px-2 py-1 rounded"
              >
                <Trash2 />
              </button>
            </div>
            </motion.div>
            </AnimatePresence>
          );
        })}
      </div>
      </div>
      )}
    
    </div>
  </div>
  )
}