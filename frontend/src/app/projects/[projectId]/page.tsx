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
import { useParams } from "next/navigation";
import { useProjects, useSelectedProject } from "@/store/projectStore";
import { getProject } from "@/app/api/project";
import { Project } from "@/types/projectVars";
import ShiftList from "@/components/rostering/ShiftList";

export default function ProjectPage(){  
  
  const params = useParams();
  const projectId = params.projectId as string;

  const { loadInstance } = useLoadInstance();
  const { loadSolutionsArray } = useLoadSolutionsArray();

  const { setSelectedProject } = useSelectedProject();
  const { projects, updateProject } = useProjects();


  const loadProject = async () => {
    try {
      
      if (projects[projectId]){
        setSelectedProject(projects[projectId]);
        return;        
      }
      const data: Project = await getProject(projectId);
      updateProject(data);
      setSelectedProject(data);

    } catch (err: any) {
      // hmmm
    }
  }

  useEffect(() => {
    loadProject();
    loadInstance();
    loadSolutionsArray();
  }, []);

  return (

    <div className="flex h-screen gap-2 overflow-hidden">
      
      {/* sidebar left*/}
      <div className="w-[20vw] min-w-[240px] max-w-[320px] border-r bg-gray-100 h-screen border-border">

        <NurseList />

        <div className="mt-2 mb-2 text-muted-foreground"></div>

        <ShiftList />
        

      </div>
      
      
      <div className="w-[70vw]">
      
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

        
        <FixVariablesSelections />
        <SolverSelector />
        <TimeLimitInput />

        <SolveButton />

      </div>
    
    </div>
  );
}