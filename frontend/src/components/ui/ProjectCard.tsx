import Link from "next/link";
import { formatDate } from "@/lib/utils";

import { Project } from "@/types/projectVars";
import EditProjectDialog from "../common/EditProjectDialog";
import DeleteProjectDialog from "../common/DeleteProjectDialog";



export default function ProjectCard({ id, name, created_at, last_modified }: Project ) {

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
        <p> Created: {formatDate(created_at)} </p> 
        <p> Last Modified: {formatDate(last_modified)} </p>
      </div>
    
      </Link>

      <div className="w-[5vw] min-w-20 flex gap-4 items-center justify-center border-l border-border mt-2 mb-2">
        
        <EditProjectDialog projectId={id} name={name} />
        
        <DeleteProjectDialog projectId={id} name={name}/>

      </div>
    </div>
  )
};