"use client";

import { useInstance } from "@/store/instanceStore";
import NurseCard from "@/components/ui/NurseCard";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search } from 'lucide-react';
import ShiftListTopbar from "../common/ShiftListTopbar";
import ShiftCard from "../ui/ShiftCard";

export default function ShiftList(){

  const [query, setQuery] = useState("");


  const { nurses, shifts } = useInstance();
  


  // filtered by search
  const filteredItems = shifts.filter((shift) =>
    shift.name.toLowerCase().includes(query.toLowerCase()) || shift.uid.toString().includes(query)
  );

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
      {filteredItems.map((shift) => (
        <AnimatePresence key={shift.uid} mode="popLayout">
          <motion.div
            key={shift.uid}
            layout
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.17 }}
            className="cursor-pointer select-none"
          >
            <ShiftCard shift={shift} key={shift.uid}/>
          </motion.div>
        </AnimatePresence>
      ))}
      </div>

  </div>
  );


}