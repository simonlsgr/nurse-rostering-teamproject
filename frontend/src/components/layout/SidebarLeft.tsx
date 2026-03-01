import { createProject } from "@/app/api/project";
import { Button } from "@/components/ui/button";
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { useState } from "react";
import { Input } from "@/components/ui/input";
import { useProjects } from "@/store/projectStore";
import { Project } from "@/types/projectVars";



export default function SidebarLeft(){


  const [openDialog, setOpenDialog] = useState<boolean>(false);
  const [nameInput, setNameInput] = useState<string>("");

  const { updateProject } = useProjects();

  const handleCreateProject = async () => {

    try {
      const res: Project = await createProject(nameInput);
      updateProject(res);
    }
    catch (err: any) {
      alert("Creation failed");
    }


  }

  return (
  
    <div className="w-[15vw] min-w-[240px] max-w-[320px] flex flex-col">

        <div className="h-[80px]">
        </div> 

        <Dialog open={openDialog} onOpenChange={setOpenDialog}>
          <DialogTrigger asChild>
            
            <Button
              className="rounded-4xl m-4 h-15 text-xl"
            >
              New project
            </Button>

          </DialogTrigger>
          <DialogContent className="w-[calc(30vw)]">
            <DialogHeader>
              <DialogTitle>Create a new project</DialogTitle>
            </DialogHeader>


            <Input
              placeholder="Name"
              value={nameInput}
              onChange={(name) =>
                setNameInput(() => ( name.target.value ))
              }
            />


            <DialogFooter className="mt-4">
              <Button
                variant="outline"
                onClick={() => {setOpenDialog(false); setNameInput("")}}
              >
                Cancel
              </Button>
              <Button onClick={() => {handleCreateProject(); setOpenDialog(false); setNameInput("")}}>
                Create
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>


    </div>


  )

}