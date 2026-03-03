import { Shift } from "@/types/nurseVars";
import { ScanSearch } from 'lucide-react';

type ShiftCardProps = {
  shift: Shift;
};


export default function ShiftCard({ shift }: ShiftCardProps){


  return (
    
    <div 
      className={`border border-gray-400 rounded-lg bg-orange-200 w-[calc(100%-1rem)] h-18 p-2 mb-2 ml-2 mt-2 shadow transition-all duration-170 ease-in-out flex items-center group`}
    >
      <div className="flex-1">
        <p className="truncate"> Name: {shift.name} </p>              
        <p> ID: {shift.uid} </p> 
      </div>

      <div>
        <ScanSearch
          className="opacity-0 group-hover:opacity-100 transition hover:bg-gray-200 rounded" 
        />
      </div>
    </div>
  );


}