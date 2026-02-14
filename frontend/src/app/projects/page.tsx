"use client";

import SidebarLeft from "@/components/layout/SidebarLeft";
import ProjectCard from "@/components/ui/ProjectCard";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

import SearchIcon from '@mui/icons-material/Search';


export default function ProjectsView(){
  
  const [query, setQuery] = useState("");
  
  const projects = [
    { id: "1", name: "Project A", num_of_nurses: 21 },
    { id: "2", name: "Project B", num_of_nurses: 32 },
  ];

  // filtered by search
  const filteredItems = projects.filter((project) =>
    project.name.toLowerCase().includes(query.toLowerCase()) || project.id.includes(query)
  );

  return (


    <div className="flex h-screen gap-2">
      
      <SidebarLeft />
      
      
      <div className="w-full">
      
        {/* topbar */}
        <div className="h-[80px] flex items-center justify-center">
          <h1 className="text-2xl font-semibold"> Nurse Rostering Solver</h1>
        </div>
      
        {/* main view */}
        <div className="p-6 rounded-tl-3xl bg-gray-100 border border-border h-[calc(100vh-80px)] overflow-auto">
      
          <h1 className="text-3xl font-semibold text-gray-600 pb-2 mb-4">
            Projects
          </h1>

          <div className="w-[calc(60%)] h-[40px] p-2 border rounded mb-10 bg-white flex gap-4 items-center">
            
            <SearchIcon />
            
            <input
              type="text"
              placeholder="Search..."
              value={query}
              onChange={(s) => setQuery(s.target.value)}
              className="text-xl focus:outline-none w-full"
            />
          </div>
      
          {/* projects list */}
          <div className="overflow-auto bg-white p-4 rounded-3xl">
            {filteredItems.map((project, idx) => (
              <AnimatePresence key={project.id} mode="popLayout">
                <motion.div
                  key={project.id}
                  layout
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ duration: 0.17 }}
                  className="cursor-pointer select-none"
                >
                  <ProjectCard key={idx} id={project.id} name={project.name} nb_nurses={project.num_of_nurses}/>
                </motion.div>
              </AnimatePresence>

            
            ))}


          </div>
       
        </div>
      
      </div>

      {/* sidebar right */}
      <div className="w-[1vw] hidden">
      </div>
    
    </div>
  );
}





