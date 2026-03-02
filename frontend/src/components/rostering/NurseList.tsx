"use client";

import { useInstance } from "@/store/instanceStore";
import NurseCard from "@/components/ui/NurseCard";
import { Nurse } from "@/types/nurseVars";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import PeopleIcon from '@mui/icons-material/People';
import AssignmentIcon from '@mui/icons-material/Assignment';


export default function NurseList(){

  const [query, setQuery] = useState("");


  const { nurses, shifts } = useInstance();
  
  

  

  // filtered by search
  const filteredItems = nurses.filter((nurse) =>
    nurse.name.toLowerCase().includes(query.toLowerCase()) || nurse.uid.toString().includes(query)
  );





  return (

    <div className="border-b h-[100vh] content-between border-border flex flex-col">
      
      <div className="p-2 flex flex-row gap-2">
        <div className="h-10 w-10" onClick={() => console.log("Nurses")}>
          <PeopleIcon className="p-2 h-full! w-full! hover:bg-gray-500 bg-black! text-white bg-white rounded-xl"/>
        </div>
        <div className="h-10 w-10" onClick={() => console.log("Nurses")}>
          <AssignmentIcon className="p-2 hover:bg-gray-500 bg-white h-full! w-full! rounded-xl"/>
        </div>
      </div>

      <input
        type="text"
        placeholder="Search..."
        value={query}
        onChange={(s) => setQuery(s.target.value)}
        className="w-[calc(100%-1rem)] ml-2 p-1 border border-gray-300 rounded focus:outline-none"
      />

      <p className="border-b m-2 border-border"></p>

      <div className="overflow-auto flex-1">
      {filteredItems.map((nurse) => (
        <AnimatePresence key={nurse.uid} mode="popLayout">
          <motion.div
            key={nurse.uid}
            layout
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.17 }}
            className="select-none"
          >
            <NurseCard nurse={nurse} key={nurse.uid}/>
          </motion.div>
        </AnimatePresence>
      ))}
      </div>

  </div>
  );


}