import { Nurse } from "@/types/nurseVars";


type NurseCardProps = {
  nurse: Nurse
};


export default function NurseCard({ nurse }: NurseCardProps){


  return (
    
    <div 
      className="border rounded-lg w-[calc(100%-1rem)] h-20 p-2 mb-2 ml-2 mt-2 bg-green-200 shadow" 
      key={nurse.id}
    >
      <p className=""> Name: {nurse.name} </p>              
      <p> ID: {nurse.id} </p> 
    </div>
  );


}