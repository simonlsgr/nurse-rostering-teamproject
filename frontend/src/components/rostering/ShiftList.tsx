"use client";

import { useInstance } from "@/store/instanceStore";
import NurseCard from "@/components/ui/NurseCard";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search } from 'lucide-react';
import ShiftListTopbar from "../common/ShiftListTopbar";
import ShiftCard from "../ui/ShiftCard";
import { useShifts } from "@/store/nurseStore";
import { Shift } from "@/types/nurseVars";
import { formatDate } from "@/lib/utils";

type ShiftListProps = {

  editShifts: boolean;
  setEditShifts: any;
  selectedItems: Shift[];
  setSelectedItems: any;
}


export default function ShiftList({ editShifts, setEditShifts, selectedItems, setSelectedItems }: ShiftListProps){

  const [query, setQuery] = useState("");

  const { shifts } = useShifts();
  

  const toggleItem = (shift: Shift) => {
    setSelectedItems((prev: Shift[]) =>
      prev.some(n => n.uid === shift.uid)
        ? prev.filter((n) => n.uid !== shift.uid)
        : [...prev, shift]
    );
  };


  // filtered by search
  const filteredItems = shifts.filter((shift) =>
    shift.name.toLowerCase().includes(query.toLowerCase()) || formatDate(shift.start_time, "date").includes(query)
  );

  const sortedItems = [
    ...filteredItems.filter((shift) => selectedItems?.some((n: Shift) => n.uid === shift.uid)),
    ...filteredItems.filter((shift) => !selectedItems?.some((n: Shift) => n.uid === shift.uid)),
  ];


  return (

    <div className="border-b h-[49vh] content-between border-border flex flex-col">

      <ShiftListTopbar />
      
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
      {(sortedItems ? sortedItems : filteredItems).map((shift) => (
        <AnimatePresence key={shift.uid} mode="popLayout">
          <motion.div
            key={shift.uid}
            layout
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.17 }}
            className="select-none"
            onClick={() => editShifts ? toggleItem(shift) : ""}
          >
            <ShiftCard 
              shift={shift} 
              key={shift.uid} 
              selectable={editShifts}
              selected={editShifts ? (selectedItems?.filter((s: Shift) => s.uid == shift.uid)[0] ? true : false) : false}
              editDemand={true}
            />
          </motion.div>
        </AnimatePresence>
      ))}
      </div>

  </div>
  );


}