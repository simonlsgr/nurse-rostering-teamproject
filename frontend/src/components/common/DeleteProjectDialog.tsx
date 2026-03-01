import { useState } from "react";
import { Button } from "../ui/button";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "../ui/dialog";
import { Input } from "../ui/input";
import { deleteProject, editProject } from "@/app/api/project";
import EditIcon from '@mui/icons-material/Edit';
import { useProjects } from "@/store/projectStore";
import DeleteIcon from '@mui/icons-material/Delete';

type DeleteDialogProps = {
  projectId: string;
  name: string;
};


export default function DeleteProjectDialog({ projectId, name }: DeleteDialogProps) {

  const [openDialog, setOpenDialog] = useState<boolean>(false);

  const { removeProject } = useProjects();

  const handleDeleteProject = async () => {

    try {
      const res = await deleteProject(projectId);
      removeProject(projectId);
    }
    catch (err: any) {
      alert("Delete failed");
    }

  }


  return (


    <Dialog open={openDialog} onOpenChange={setOpenDialog}>
      <DialogTrigger asChild>
        
        <DeleteIcon
          fontSize="small" 
          className="hover:bg-gray-200 rounded"
        />

      </DialogTrigger>
      <DialogContent className="w-[calc(30vw)]">
        <DialogHeader>
          <DialogTitle>Delete project {name}</DialogTitle>
        </DialogHeader>

        Are you sure you want to delete this project?

        <DialogFooter className="mt-4">
          <Button
            variant="outline"
            onClick={() => {setOpenDialog(false);}}
          >
            Cancel
          </Button>
          <Button variant={"destructive"} onClick={() => {handleDeleteProject(); setOpenDialog(false)}}>
            Delete
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    
  )
}