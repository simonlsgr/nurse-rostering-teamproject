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

type CalendarProps = {
  selectedDates: Date[];
  setSelectedDates: any;
}



export default function DetailViewEditDaysOffCalendar({ selectedDates, setSelectedDates }: CalendarProps) {
  const [dates, setDates] = useState<Date[] | undefined>(selectedDates);
  const [openPopover, setOpenPopover] = useState<boolean>(false);

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
            before: new Date("2018-01-01"), // TODO: link to planning horizon
            after: new Date("2018-01-14")
          }}
          startMonth={ new Date(2018, 0) } // here too
          endMonth={ new Date(2018, 0) }
          defaultMonth={ new Date("2018-01-01") }
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