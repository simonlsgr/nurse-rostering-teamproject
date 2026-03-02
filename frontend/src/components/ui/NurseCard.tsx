import { Nurse } from "@/types/nurseVars";


type NurseCardProps = {
  nurse: Nurse
};


export default function NurseCard({ nurse }: NurseCardProps){



  return (
    
    <div 
      className={`border border-gray-400 rounded-lg w-[calc(100%-1rem)]  p-2 mb-2 ml-2 mt-2 bg-green-200 hover:bg-green-100 shadow transition-all duration-170 ease-in-out`}
    >
      <p className="truncate"> Name: {nurse.name} </p>              
      <p> Worktime: {nurse.minimum_work_time/60}h - {nurse.maximum_work_time/60}h </p>
      <p className="truncate"> Min. Consecutive Shifts: {nurse.minimum_consecutive_days_off}</p> 
      <p className="truncate"> Max. Consecutive Shifts: {nurse.maximum_consecutive_shifts}</p> 
    </div>
  );


}