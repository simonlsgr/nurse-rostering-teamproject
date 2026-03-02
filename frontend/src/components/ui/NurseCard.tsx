import { useNurseListSelection } from "@/store/nurseStore";
import { Nurse } from "@/types/nurseVars";
import { ScanSearch } from 'lucide-react';

type NurseCardProps = {
  nurse: Nurse
};


export default function NurseCard({ nurse }: NurseCardProps){

  const { selectedNurses } = useNurseListSelection();


  return (
    
    <div 
      className={`border border-gray-400 rounded-lg w-[calc(100%-1rem)] h-18 p-2 mb-2 ml-2 mt-2 ${selectedNurses.some(n => n.uid === nurse.uid) ? "bg-pink-200 hover:bg-pink-100" : "bg-green-200 hover:bg-green-100"} shadow transition-all duration-170 ease-in-out flex items-center group`}
    >
      <div className="flex-1">
        <p className="truncate"> Name: {nurse.name} </p>              
        <p> ID: {nurse.uid} </p> 
      </div>

      <div>
        <ScanSearch
          className="opacity-0 group-hover:opacity-100 transition hover:bg-gray-200 rounded" 
        />
      </div>
    </div>
  );


}