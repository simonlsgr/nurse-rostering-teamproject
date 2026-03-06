import { useState } from "react";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "../ui/dialog";
import { Button } from "../ui/button";
import AddIcon from '@mui/icons-material/Add';
import { Input } from "../ui/input";
import { Nurse } from "@/types/nurseVars";



export default function CreateNurseDialog() {

  const [openDialog, setOpenDialog] = useState<boolean>(false);

  const [newNurse, setNewNurse] = useState<Nurse>(
    {
      uid: 0,
      name: "",
      preferred_shifts: [],
      preferred_off_shifts: [],
      blocked_shifts: [],
      days_off: [],
      staff: false,
      min_time_between_shifts: "",
      preferred_shift_weight: {},
      preferred_off_shift_weight: {},
      minimum_work_time: 0,
      maximum_work_time: 0,
      minimum_consecutive_shifts: 0,
      maximum_consecutive_shifts: 0,
      minimum_consecutive_days_off: 0,
      maximum_weekends: 0,
      maximum_number_of_shifts_per_type: {},
    }
  )


  return (

    <Dialog open={openDialog} onOpenChange={setOpenDialog}>
      <DialogTrigger asChild>
        
      <AddIcon
        fontSize="small"
        className="hover:bg-gray-200 rounded text-muted-foreground"
      />

      </DialogTrigger>
      <DialogContent className="!w-[90vw] !max-w-[1200px] h-[calc(80vh)]">
        <DialogHeader>
          <DialogTitle>Create a new nurse</DialogTitle>
        </DialogHeader>

          <Input
            placeholder="Name"
            value={newNurse.name}
            onChange={(e) =>
              setNewNurse((n: any) => ({ ...n, name: e.target.value }))
            }
          />




        <DialogFooter className="mt-4 flex items-end">
          <Button
            variant="outline"
            onClick={() => {setOpenDialog(false);}}
          >
            Cancel
          </Button>
          <Button onClick={() => {setOpenDialog(false)}}>
            Create
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    
  )
}