import { createProject } from "@/app/api/project";
import { Button } from "@/components/ui/button";
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { createDefaultNewProject } from "@/lib/utils";
import { useNewProject, useProjects } from "@/store/projectStore";
import { Project } from "@/types/projectVars";
import { capitalize } from "@mui/material";
import { useEffect, useState } from "react";
import PlanningHorizonInput from "./PlanningHorizonInput";
import ShiftTypesInput from "./ShiftTypesInput";
import NotFollowedByShiftTypesInput from "./NotFollowedByShiftTypesInput";



export default function CreateProjectDialog(){

  const [openDialog, setOpenDialog] = useState<boolean>(false);

  const { newProject, setNewProject } = useNewProject();
  const { updateProject } = useProjects();


  useEffect(() => {
    
    setNewProject(createDefaultNewProject());

  }, [openDialog])


  const handleCreateProject = async () => {

    try {

      const { shift_types, ...project } = newProject;

      const res: Project = await createProject(project as Project);
      updateProject(res);
    }
    catch (err: any) {
      alert("Creation failed");
    }


  }

  return (
    <Dialog open={openDialog} onOpenChange={setOpenDialog}>
    <DialogTrigger asChild>
      
      <Button
        className="rounded-4xl m-4 h-15 text-xl"
      >
        New project
      </Button>

    </DialogTrigger>
    <DialogContent className="!max-w-none w-[48vw] h-[80vh] bg-gray-100">
      <DialogHeader>
        <DialogTitle>Create a new project</DialogTitle>
      </DialogHeader>

      <div className="overflow-auto flex flex-col gap-4 pr-2">

        <div className="rounded-2xl bg-white p-3">
          <p className="font-semibold mb-2"> Name: </p>
            <div className="">
              <input
                className="border border-border rounded-md p-1 mb-2"
                value={newProject.name}
                onChange={(e) =>
                  setNewProject(prev => ({...prev, "name": e.target.value}))
                }
              />
          </div>
        </div>
        
        <div className="rounded-2xl bg-white p-3">
          <PlanningHorizonInput />
        </div>
      
        <div className="rounded-2xl bg-white p-3">
          <ShiftTypesInput />
        </div>

        <div className="rounded-2xl bg-white p-3">
          <NotFollowedByShiftTypesInput />
        </div>

      {JSON.stringify(newProject)}
      </div>

      <DialogFooter className="mt-4 flex items-end">
        <Button
          variant="outline"
          onClick={() => {setOpenDialog(false); setNewProject(createDefaultNewProject())}}
        >
          Cancel
        </Button>
        <Button onClick={() => {handleCreateProject(); setOpenDialog(false); setNewProject(createDefaultNewProject())}}>
          Create
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
  )
}