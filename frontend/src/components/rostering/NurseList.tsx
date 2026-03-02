"use client";

import { useNurseListSelection } from "@/store/nurseStore";
import { useInstance } from "@/store/instanceStore";
import NurseCard from "@/components/ui/NurseCard";
import { Nurse } from "@/types/nurseVars";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search } from 'lucide-react';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import AddIcon from '@mui/icons-material/Add';

export default function NurseList(){

  const [query, setQuery] = useState("");


  const { nurses, shifts } = useInstance();
  const { selectedNurses, setSelectedNurses } = useNurseListSelection();
  

  const toggleItem = (nurse: Nurse) => {
    setSelectedNurses((prev) =>
      prev.some(n => n.uid === nurse.uid)
        ? prev.filter((n) => n.uid !==nurse.uid)
        : [...prev, nurse]
    );
  };

  // filtered by search
  const filteredItems = nurses.filter((nurse) =>
    nurse.name.toLowerCase().includes(query.toLowerCase()) || nurse.uid.toString().includes(query)
  );

  // sort items by selection
  const sortedItems = [
    ...filteredItems.filter((nurse) => selectedNurses.some(n => n.uid === nurse.uid)),
    ...filteredItems.filter((nurse) => !selectedNurses.some(n => n.uid === nurse.uid)),
  ];




  return (

    <div className="border-b h-[50vh] content-between border-border flex flex-col">
      <div className="flex justify-between items-center pr-1">
        <p className="p-2"> All Nurses: </p>

        <div className="flex gap-1">
          <AddIcon 
            fontSize="small"
            className="hover:bg-gray-200 rounded text-muted-foreground"
          />
          <MoreVertIcon 
            fontSize="small"
            className="hover:bg-gray-200 rounded"          
          /> 
        </div>
      
      </div>
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
      {sortedItems.map((nurse) => (
        <AnimatePresence key={nurse.uid} mode="popLayout">
          <motion.div
            key={nurse.uid}
            layout
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.17 }}
            className="cursor-pointer select-none"
            onClick={() => toggleItem(nurse)}
          >
            <NurseCard nurse={nurse} key={nurse.uid}/>
          </motion.div>
        </AnimatePresence>
      ))}
      </div>

  </div>
  );


}