"use client";

import NurseList from "@/components/rostering/NurseList";
import { useLoadNurses } from "@/hooks/nurseHooks";
import { useEffect } from "react";
import InputJson from "@/components/common/InputJson"
import SolveButton from "@/components/rostering/SolveButton";
import { TabsContent, TabsList, TabsTrigger, Tabs } from "@/components/ui/tabs"
import { MainView } from "@/components/layout/MainView";
import JobsView from "@/components/layout/JobsView";


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
        
        <Tabs defaultValue="dashboard">
        
          <div className="flex justify-center">
            <TabsList>

              <TabsTrigger value="dashboard"> Dashboard </TabsTrigger>
              <TabsTrigger value="jobs"> Jobs </TabsTrigger>

            </TabsList>
          </div>
        
          <TabsContent value="dashboard">
            <MainView />
          </TabsContent>
          
          <TabsContent value="jobs">
            <JobsView />        
          </TabsContent>
        
        </Tabs>
        
        </div>
      
      </div>

      {/* sidebar right */}
      <div className="w-[20vw] min-w-[240px] max-w-[320px] border-l border-border">

        <SolveButton />

      </div>
    
    </div>
  );
}