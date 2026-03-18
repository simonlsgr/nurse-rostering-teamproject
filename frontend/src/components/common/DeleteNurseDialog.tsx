import { useState } from "react";
import { Button } from "../ui/button";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "../ui/dialog";
import { Input } from "../ui/input";
import { deleteProject, editProject } from "@/app/api/project";
import EditIcon from '@mui/icons-material/Edit';
import { useProjects, useSelectedProject } from "@/store/projectStore";
import DeleteIcon from '@mui/icons-material/Delete';
import { useDetailViewNurse, useNurses } from "@/store/nurseStore";
import { deleteNurse } from "@/app/api/nurse";


export default function DeleteNurseDialog() {

  const [openDialog, setOpenDialog] = useState<boolean>(false);

  const { detailViewNurse, setDetailViewNurse } = useDetailViewNurse();
  const { removeNurse } = useNurses();
  const { selectedProject } = useSelectedProject();

  const handleDeleteNurse = async () => {

    if(!detailViewNurse || !selectedProject) return;

    try {
      console.log(detailViewNurse.id, selectedProject.id);
      const res = await deleteNurse(detailViewNurse.id, selectedProject.id);
      removeNurse(detailViewNurse.uid);
    }
    catch (err: any) {
      alert(err ?? "Delete failed");
    }

  }


  if(!detailViewNurse || !selectedProject) return;

  return (


    <Dialog open={openDialog} onOpenChange={setOpenDialog}>
      <DialogTrigger asChild>
        

        <Button 
          className="rounded-2xl w-25"
          variant={"destructive"}
        >
          Delete
        </Button>

      </DialogTrigger>
      <DialogContent className="w-[calc(30vw)]">
        <DialogHeader>
          <DialogTitle>Delete Nurse {detailViewNurse.name}</DialogTitle>
        </DialogHeader>

        Are you sure you want to delete this nurse?

        <DialogFooter className="mt-4">
          <Button
            variant="outline"
            onClick={() => {setOpenDialog(false);}}
          >
            Cancel
          </Button>
          <Button variant={"destructive"} onClick={() => {handleDeleteNurse(); setDetailViewNurse(null); setOpenDialog(false)}}>
            Delete
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    
  )
}