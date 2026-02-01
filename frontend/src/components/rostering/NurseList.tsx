import { useNurses } from "@/store/nurseStore";
import NurseCard from "../ui/NurseCard";


export default function NurseList(){

  const { nurses } = useNurses();

  
  return (

    <div className="border-b h-[50vh] content-between overflow-auto">
      <p className="p-2"> All Nurses: </p>

      {nurses.map((nurse) => (

        <NurseCard nurse={nurse} key={nurse.id}/>

      ))}

  </div>
  );


}