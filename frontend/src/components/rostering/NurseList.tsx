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

  // filtered by search
  const filteredItems = nurses.filter((nurse) =>
    nurse.name.toLowerCase().includes(query.toLowerCase()) || nurse.id.includes(query)
  );

  // sort items by selection
  const sortedItems = [
    ...filteredItems.filter((nurse) => selectedNurses.some(n => n.id === nurse.id)),
    ...filteredItems.filter((nurse) => !selectedNurses.some(n => n.id === nurse.id)),
  ];




  return (

    <div className="border-b h-[50vh] content-between overflow-auto">
      <p className="p-2"> All Nurses: </p>

      <input
        type="text"
        placeholder="Search..."
        value={query}
        onChange={(s) => setQuery(s.target.value)}
        className="w-[calc(100%-1rem)] ml-2 p-1 border rounded focus:outline-none"
      />


      {sortedItems.map((nurse) => (
        <AnimatePresence key={nurse.id} mode="popLayout">
          <motion.div
            key={nurse.id}
            layout
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.17 }}
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