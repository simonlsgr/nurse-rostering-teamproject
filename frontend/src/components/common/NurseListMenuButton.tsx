import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import MoreVertIcon from '@mui/icons-material/MoreVert';
import NursesJSONInput from "./NursesJSONInput";
import { useState } from "react";


export default function NurseListMenuButton() {

  const [openPopover, setOpenPopover] = useState<boolean>(false);

  return (

    <Popover open={openPopover} onOpenChange={setOpenPopover}>
      <PopoverTrigger asChild>
        <MoreVertIcon 
          fontSize='small'
          className='hover:bg-gray-200 rounded' 
        />
      </PopoverTrigger>

      <PopoverContent className="w-40 h-auto text-sm border-border">
        <div className="flex flex-col gap-2 items-center">
          <NursesJSONInput />
        </div>
      </PopoverContent>
    </Popover>


  )
}