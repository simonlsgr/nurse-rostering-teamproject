import { useDetailViewNurse, useEditAttributes, useOpenNurseDetailView } from "@/store/nurseStore";
import { Nurse } from "@/types/nurseVars";
import { ScanSearch } from 'lucide-react';

type NurseCardProps = {
  nurse: Nurse
};


export default function NurseCard({ nurse }: NurseCardProps){

  const { setDetailViewNurse } = useDetailViewNurse();
  const { setOpenNurseDetailView } = useOpenNurseDetailView();
  const { setEditAttributes } = useEditAttributes();


  return (
    
    <div 
      className={`border border-gray-400 rounded-lg w-[calc(100%-1rem)] p-2 mb-2 ml-2 mt-2 shadow transition-all duration-170 ease-in-out flex items-center group bg-green-200 hover:bg-green-100`}
    >
      <div className="flex-1">
        <p className="truncate"> Name: {nurse.name} </p>              
        <p> Worktime: {nurse.minimum_work_time/60}h - {nurse.maximum_work_time/60}h </p>
        <p className="truncate"> Min. Consecutive Shifts: {nurse.minimum_consecutive_days_off}</p> 
        <p className="truncate"> Max. Consecutive Shifts: {nurse.maximum_consecutive_shifts}</p> 
      </div>

      <div>
        <ScanSearch
          className="opacity-0 group-hover:opacity-100 transition hover:bg-gray-200 rounded" 
          onClick={() => { setDetailViewNurse(nurse); setOpenNurseDetailView(true); setEditAttributes({}); }}
        />
      </div>
    </div>
  );


}