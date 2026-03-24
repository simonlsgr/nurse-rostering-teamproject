import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useEffect, useState } from "react";



type Props = {
  jsonInput: any,
  setJsonInput: any,
}


export default function ProjectJSONInput({ jsonInput, setJsonInput }: Props) {



  return (

        <div className="flex flex-col gap-3 overflow-auto">
          <Textarea
            value={jsonInput}
            onChange={(e) => setJsonInput(e.target.value)}
            className="min-h-[200px] h-[60vh]"
          />

        </div>

  )
}
