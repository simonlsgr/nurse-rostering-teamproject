import { useState } from "react";
import { Button } from "../ui/button";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "../ui/dialog";
import { Input } from "../ui/input";
import { editProject } from "@/app/api/project";
import EditIcon from '@mui/icons-material/Edit';
import { useProjects } from "@/store/projectStore";

type EditDialogProps = {
  projectId: string;
  name: string;
};


export default function EditProjectDialog({ projectId, name }: EditDialogProps) {

  const [openDialog, setOpenDialog] = useState<boolean>(false);
  const [nameInput, setNameInput] = useState<string>(name);

  const { updateProject } = useProjects();

  const handleEditProject = async () => {

    try {
      const res = await editProject(projectId, nameInput);
      updateProject(res);
    }
    catch (err: any) {
      alert("Edit failed");
    }

  }


  return (


    <Dialog open={openDialog} onOpenChange={setOpenDialog}>
      <DialogTrigger asChild>
        
        <EditIcon
          fontSize="small" 
          className="hover:bg-gray-200 rounded"
        />

      </DialogTrigger>
      <DialogContent className="w-[calc(30vw)]">
        <DialogHeader>
          <DialogTitle>Edit project {name}</DialogTitle>
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
          <Button onClick={() => {handleEditProject(); setOpenDialog(false); setNameInput("")}}>
            Save
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    
  )
}