import { useNurseListSelection } from "@/store/nurseStore";
import { Nurse } from "@/types/nurseVars";


type NurseCardProps = {
  nurse: Nurse
};


export default function NurseCard({ nurse }: NurseCardProps){

  const { selectedNurses } = useNurseListSelection();


  return (
    
    <div 
      className={`border border-gray-400 rounded-lg w-[calc(100%-1rem)] h-18 p-2 mb-2 ml-2 mt-2 ${selectedNurses.some(n => n.id === nurse.id) ? "bg-pink-200 hover:bg-pink-100" : "bg-green-200 hover:bg-green-100"} shadow transition-all duration-170 ease-in-out`}
    >
      <p className="truncate"> Name: {nurse.name} </p>              
      <p> ID: {nurse.id} </p> 
    </div>
  );


}