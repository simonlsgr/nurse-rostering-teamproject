"use client";

import { useState } from "react";
import { Calendar } from "@/components/ui/calendar";
import { Button } from "@/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { CalendarDays } from 'lucide-react';
import { useSelectedProject } from "@/store/projectStore";

type CalendarProps = {
  selectedDates: Date[];
  setSelectedDates: any;
}



export default function DetailViewEditDaysOffCalendar({ selectedDates, setSelectedDates }: CalendarProps) {
  const [dates, setDates] = useState<Date[] | undefined>(selectedDates);
  const [openPopover, setOpenPopover] = useState<boolean>(false);

  const { selectedProject } = useSelectedProject();
  const planningHorizon = selectedProject?.planning_horizon ?? ["2018-01-01", "2018-01-01"];


  return (
    <Popover open={openPopover} onOpenChange={setOpenPopover}>
      <PopoverTrigger asChild>
        <CalendarDays 
          fontSize={"small"} 
          className="transition-all duration-170 ease-in-out hover:bg-gray-100 rounded-lg"
        />
      </PopoverTrigger>

      <PopoverContent className="w-auto p-0 flex flex-col items-end">
        <Calendar
          mode="multiple"
          selected={dates}
          onSelect={setDates}
          hidden={{
            before: new Date(planningHorizon[0]),
            after: new Date(planningHorizon[1])
          }}
          startMonth={ new Date(planningHorizon[0]) }
          endMonth={ new Date(planningHorizon[1]) }
          defaultMonth={ new Date(planningHorizon[0]) }
        />
        <Button 
          className="m-2 mt-0"
          onClick={() => {setSelectedDates(dates); setOpenPopover(false)}}
          >
          Save
        </Button>
      </PopoverContent>
    </Popover>
  );
}

// border border-border rounded-lg mb-2