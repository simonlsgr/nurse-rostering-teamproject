'use client';




import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { SolutionViewer } from "@/components/rostering/SolutionViewer";
import { VariableFixer } from "@/components/rostering/VariableFixer";


export function MainView(){
  
  
  

  return (
    <div className="flex flex-col p-4 gap-4 h-full w-full">
      
        
      <h1 className="text-2xl font-bold pb-2 mb-4 border-b border-border">
        Project [id]
      </h1>
      <Tabs defaultValue="fix_vars">
      
        <div className="flex justify-center">
          <TabsList>

            <TabsTrigger value="solution_viewer"> Solution Viewer </TabsTrigger>
            <TabsTrigger value="fix_vars"> Fix Variables </TabsTrigger>

          </TabsList>
        </div>
        <div className="p-4 flex flex-col gap-4 w-full h-[80vh] overflow-y-scroll">
      
          <TabsContent value="solution_viewer">
            <SolutionViewer />
          </TabsContent>
          
          <TabsContent value="fix_vars">
            <VariableFixer />
          </TabsContent>
        </div>
      </Tabs>
      
      
        
      
    </div>
  );
}
