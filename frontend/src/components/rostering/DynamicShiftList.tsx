"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search, ToggleLeft } from 'lucide-react';
import ShiftListTopbar from "../common/ShiftListTopbar";
import ShiftCard from "../ui/ShiftCard";
import { Nurse, Shift } from "@/types/nurseVars";
import { AnyMxRecord } from "dns";
import { formatDate } from "@/lib/utils";
import { shiftUid } from "@/types/feasibilityHelperVars";
import { init } from "next/dist/compiled/webpack/webpack";


type DynamicShiftListProps = {
  shifts: Shift[];
  shift_weights?: Record<string, number>;
  setShiftWeight?: any;
  selectable?: boolean;
  selectedItems?: any;
  setSelectedItems?: any;
}


export default function DynamicShiftList({ shifts, shift_weights, setShiftWeight, selectable = false, selectedItems = null, setSelectedItems = null }: DynamicShiftListProps) {

  const [query, setQuery] = useState("");


  const toggleItem = (shift: Shift) => {
    setSelectedItems((prev: Shift[]) =>
      prev.some(n => n.uid === shift.uid)
        ? prev.filter((n) => n.uid !== shift.uid)
        : [...prev, shift]
    );
  };


  const filteredItems = shifts.filter((shift) =>
    shift.name.toLowerCase().includes(query.toLowerCase()) || formatDate(shift.start_time, "date").includes(query)
  );

  
  const sortedItems = [
    ...filteredItems.filter((shift) => selectedItems?.some((n: Shift) => n.uid === shift.uid)),
    ...filteredItems.filter((shift) => !selectedItems?.some((n: Shift) => n.uid === shift.uid)),
  ];


  const handleCardSelect = (shift: Shift, initWeight: boolean) => {

    toggleItem(shift);
    if (!setShiftWeight) return;
    if (initWeight) {
      setShiftWeight(1, shift);
    } else {
      setShiftWeight(0, shift, true)
    }

  }

  if (shifts.length <= 0) return (
    <div className="text-muted-foreground italic flex justify-center">
      No Entries
    </div>
  )

  if ( selectable && (!selectedItems || !setSelectedItems)) {
    return;
  }

  return(

    <div className="content-between border-border flex flex-col">
      
      <div className="flex w-[calc(100%-1rem)] ml-2 p-1 border border-gray-300 rounded">
        <input
          type="text"
          placeholder="Search..."
          value={query}
          onChange={(s) => setQuery(s.target.value)}
          className="flex-1 focus:outline-none"
        />
        <Search fontSize={"small"} />
      </div>
      
      <p className="border-b m-2 border-border"></p>

      <div className="overflow-auto flex-1">
      {(selectable ? sortedItems : filteredItems).map((shift) => (
        <AnimatePresence key={shift.uid} mode="popLayout">
          <motion.div
            key={shift.uid}
            layout
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.17 }}
            className={`select-none`}
            onClick={() => selectable ? handleCardSelect(shift, selectedItems?.filter((s: Shift) => s.uid == shift.uid)[0] ? false : true) : ""}
          >
            <ShiftCard 
              shift={shift}
              weight={shift_weights ? shift_weights[shift.uid] : undefined} 
              setWeight={setShiftWeight}
              selectable={selectable} 
              selected={selectedItems?.filter((s: Shift) => s.uid == shift.uid)[0] ? true : false} 
              key={shift.uid}
            />
          </motion.div>
        </AnimatePresence>
      ))}
      </div>

  </div>
  );

}