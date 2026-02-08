"use client";

import NurseList from "@/components/rostering/NurseList";
import { useLoadNurses } from "@/hooks/nurseHooks";
import { useEffect } from "react";
import InputJson from "@/components/common/InputJson"
import SolveButton from "@/components/rostering/SolveButton";

export default function ProjectPage({ params }: { params: { projectId: string } }){  
  
  const { loadNurses } = useLoadNurses();



  useEffect(() => {
    loadNurses();
  }, []);




  return (

    <div className="flex h-screen gap-2 overflow-hidden">
      
      {/* sidebar left*/}
      <div className="w-[20vw] min-w-[240px] max-w-[320px] border-r bg-gray-100 h-screen border-border">

        <NurseList />
        
        <InputJson />

      </div>
      
      
      <div className="w-full">
      
        {/* topbar */}
        <div className="h-[2vw] min-h-[30px] max-h-[40px] hidden">
        </div>
      
        {/* main view */}
        <div className="p-2">
      
          <h1 className="text-2xl font-bold pb-2 mb-4 border-b border-border">
            Project [id]
          </h1>
      
       
        </div>
      
      </div>

      {/* sidebar right */}
      <div className="w-[20vw] min-w-[240px] max-w-[320px] border-l border-border">

        <SolveButton />

      </div>
    
    </div>
  );
}