"use client";

import NurseList from "@/components/rostering/NurseList";
import { useLoadInstance } from "@/hooks/instanceHooks";
import { useLoadSolutionsArray } from "@/hooks/solutionHooks";
import { use, useEffect } from "react";
import SolveButton from "@/components/rostering/SolveButton";
import FixVariablesSelections from "@/components/rostering/FixVariablesSelection";
import SolverSelector from "@/components/rostering/SolverSelector";
import TimeLimitInput from "@/components/rostering/TimeLimitInput";
import { TabsContent, TabsList, TabsTrigger, Tabs } from "@/components/ui/tabs"
import { MainView } from "@/components/layout/MainView";
import JobsView from "@/components/layout/JobsView";
import { SolutionViewer } from "@/components/rostering/SolutionViewer";
import { VariableFixer } from "@/components/rostering/VariableFixer";


export default function ProjectPage({ params }: { params: { projectId: string } }){  
  
  const { loadInstance } = useLoadInstance();
  const { loadSolutionsArray } = useLoadSolutionsArray();

  useEffect(() => {
    loadInstance();
    loadSolutionsArray();
  }, []);




  return (

    <div className="flex h-screen gap-2 overflow-hidden">
      
      {/* sidebar left*/}
      <div className="w-[20vw] min-w-[240px] max-w-[320px] border-r bg-gray-100 h-screen border-border">

        <NurseList />
        
        

      </div>
      
      
      <div className="w-full">
      
        {/* topbar */}
        <div className="h-[2vw] min-h-[30px] max-h-[40px] hidden">
        </div>
      
        {/* main view */}
        <div className="p-2">
        
        <Tabs defaultValue="solution_viewer">
        
          <div className="flex justify-center">
            <TabsList>

              <TabsTrigger value="solution_viewer"> View Solutions </TabsTrigger>
              <TabsTrigger value="create_job"> Solve </TabsTrigger>
              <TabsTrigger value="jobs"> Jobs </TabsTrigger>

            </TabsList>
          </div>
        
          <TabsContent value="solution_viewer">
            <SolutionViewer />
          </TabsContent>
                    
          <TabsContent value="create_job">
            <VariableFixer />
          </TabsContent>
          
          <TabsContent value="jobs">
            <JobsView />        
          </TabsContent>
        
        </Tabs>
        
        </div>
      
      </div>

      
    
    </div>
  );
}