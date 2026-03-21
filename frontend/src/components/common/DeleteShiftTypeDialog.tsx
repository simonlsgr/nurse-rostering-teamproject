

import { useEffect, useState } from "react";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "../ui/dialog";
import { Button } from "../ui/button";
import ShiftTypesEditor from "./ShiftTypesEditor";
import { useShiftTypes } from "@/store/projectStore";
import NotFollowedByShiftTypesInput from "./NotFollowedByShiftTypesInput";
import NotFollowedByShiftTypesEditor from "./NotFollowedByShiftTypesEditor";
import { ShiftType } from "@/types/projectVars";
import { Trash2 } from "lucide-react";



type DeleteProps = {

  shiftType: ShiftType;
  deleteShiftType: any;
}

export default function DeleteShiftTypeDialog({ shiftType, deleteShiftType }: DeleteProps) {
  const [openDialog, setOpenDialog] = useState<boolean>(false);
  

  return (
    <Dialog open={openDialog} onOpenChange={setOpenDialog}>
      <DialogTrigger asChild>

            <button
              className="text-red-500 hover:bg-red-100 px-2 py-1 rounded"
            >
              <Trash2 />
            </button>

      </DialogTrigger>
      <DialogContent className="!w-[20vw] !max-w-[1200px] h-[calc(20vh)]">
        <DialogHeader className="h-min">
          <DialogTitle>Delete Shift Type</DialogTitle>
        </DialogHeader>

        <div>
          Delete this shift type?
        </div>

        <DialogFooter className="mt-4 flex items-end">
          <Button
            onClick={() => setOpenDialog(false)}
          >
            Cancel
          </Button>
          
          <Button 
            variant={"destructive"}
            onClick={() => deleteShiftType(shiftType.id)}
          >
            Delete
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}