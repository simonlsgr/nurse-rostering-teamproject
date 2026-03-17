import { formatDate } from "@/lib/utils";
import { Shift } from "@/types/nurseVars";
import { ScanSearch } from 'lucide-react';

type ShiftCardProps = {
  shift: Shift;
  weight?: number;
  selectable?: boolean;
  selected?: boolean;
};


export default function ShiftCard({ shift, weight, selectable = false, selected = false }: ShiftCardProps){

  return (
    
    <div 
      className={`border border-gray-400 rounded-lg w-[calc(100%-1rem)] h-auto p-2 mb-2 ml-2 mt-2 shadow transition-all duration-170 ease-in-out flex items-center ${selectable && "hover:bg-orange-100"} ${selected ? "bg-red-200 hover:bg-red-100" : ""} bg-orange-200`}
    >
      <div className="flex-1 overflow-auto">
        <div className="">
          <p className="truncate font-semibold"> Shift {shift.name} </p>              
          <p> {formatDate(shift.start_time, "weekday")}. {formatDate(shift.start_time, "date")}</p>
        </div>
        {/* <p> Time: {formatDate(shift.start_time, "time")} - {formatDate(shift.end_time, "time")}</p>  */}
        {weight && (
        <p> Weight: {weight} </p>
        )}
      </div>

      {/* <div>
        <ScanSearch
          className="opacity-0 group-hover:opacity-100 transition hover:bg-gray-200 rounded" 
        />
      </div> */}
    </div>
  );


}