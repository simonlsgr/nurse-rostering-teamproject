"use client";

import NurseList from "@/components/rostering/NurseList";
import { useLoadNurses } from "@/hooks/nurseHooks";
import { useEffect } from "react";


export default function ProjectPage({ params }: { params: { projectId: string } }){  
  
  const { loadNurses } = useLoadNurses();


  useEffect(() => {
    loadNurses();
  }, []);



  return (

    <div className="flex h-screen gap-2">
      
      {/* sidebar left*/}
      <div className="w-[10vw] min-w-[240px] max-w-[320px] border-r bg-gray-200">

        <NurseList />


      </div>
      
      
      <div className="w-full">
      
        {/* topbar */}
        <div className="h-[2vw] min-h-[30px] max-h-[40px] hidden">
        </div>
      
        {/* main view */}
        <div className="p-2">
      
          <h1 className="text-2xl font-bold pb-2 mb-4 border-b">
            Project [id]
          </h1>
      
       
        </div>
      
      </div>

      {/* sidebar right */}
      <div className="w-[10vw] min-w-[240px] max-w-[320px] border-l">



      </div>
    
    </div>
  );
}