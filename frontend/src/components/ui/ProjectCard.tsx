import Link from "next/link";

import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';



type ProjectCardProps = {
  id: string;
  name: string;
  nb_nurses: number;
};

export default function ProjectCard({ id, name, nb_nurses }: ProjectCardProps ) {

  return (
    <div 
      className="border rounded-xl w-full h-25 p-3 pt-2 mb-4 bg-white hover:bg-gray-100 transition duration-130 flex"
      key={id}
    >
      <Link 
          href={`/projects/${id}`}
          key={id}
          className="text-xl flex-1"
      >
        {name}
      
      <div className="pt-1 text-base">
        <p> ID: {id} </p> 
        <p> Nurses: {nb_nurses} </p>
      </div>
    
      </Link>

      <div className="w-[5vw] min-w-20 flex gap-4 items-center justify-center border-l border-border mt-2 mb-2">
        
        <EditIcon fontSize="small" className="hover:bg-gray-200 rounded"/>
        <DeleteIcon fontSize="small" className="hover:bg-gray-200 rounded"/>

      </div>
    </div>
  )
};