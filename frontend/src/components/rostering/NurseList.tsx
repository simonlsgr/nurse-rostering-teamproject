import { useNurseListSelection, useNurses } from "@/store/nurseStore";
import NurseCard from "../ui/NurseCard";
import { Nurse } from "@/types/nurseVars";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";


export default function NurseList(){

  const [query, setQuery] = useState("");


  const { nurses } = useNurses();
  const { selectedNurses, setSelectedNurses } = useNurseListSelection();
  

  const toggleItem = (nurse: Nurse) => {
    setSelectedNurses((prev) =>
      prev.some(n => n.id === nurse.id)
        ? prev.filter((n) => n.id !==nurse.id)
        : [...prev, nurse]
    );
  };


  const filteredItems = nurses.filter((nurse) =>
    nurse.name.toLowerCase().includes(query.toLowerCase()) || nurse.id.includes(query)
  );


  const sortedItems = [
    ...filteredItems.filter((nurse) => selectedNurses.some(n => n.id === nurse.id)),
    ...filteredItems.filter((nurse) => !selectedNurses.some(n => n.id === nurse.id)),
  ];




  return (

    <div className="border-b h-[50vh] content-between overflow-auto">
      <p className="p-2"> All Nurses: </p>

      {sortedItems.map((nurse) => (
        <AnimatePresence key={nurse.id}>
          <motion.div layout
            key={nurse.id} 
            className="cursor-pointer select-none"
            onClick={() => toggleItem(nurse)}
          >
            <NurseCard nurse={nurse} key={nurse.id}/>
          </motion.div>
        </AnimatePresence>
      ))}


  </div>
  );


}