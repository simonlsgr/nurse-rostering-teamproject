import Link from "next/link";
import { formatDate } from "@/lib/utils";

import { Project } from "@/types/projectVars";
import EditProjectDialog from "../common/EditProjectDialog";
import DeleteProjectDialog from "../common/DeleteProjectDialog";
import { useSelectedProject } from "@/store/projectStore";


type ProjectCardProps = {
  project: Project;
}

export default function ProjectCard({ project }: ProjectCardProps) {

  const { id, name, created_at, last_modified, planning_horizon } = project;

  const { setSelectedProject } = useSelectedProject();

  return (
    <div 
      className="border rounded-xl w-full h-25 p-3 pt-2 mb-4 bg-white hover:bg-gray-100 transition duration-130 flex"
      key={id}
    >
      <Link 
          href={`/projects/${id}`}
          key={id}
          className="text-2xl flex-1"
          //onClick={() => setSelectedProject(project)}
      >
        {name}
      
      <div className="pt-1 text-base flex h-13">
        <div className="flex-1 flex items-end">
          
          <div className="pl-4"> 
            <div className="flex gap-2">
              <p className="text-muted-foreground">
                Planning Start: 
              </p>
              <p className="pl-[1px]">
                {formatDate(planning_horizon[0], "date")}
              </p>
            </div>
            <div className="flex gap-4">
            <p className="text-muted-foreground">
              Planning End: 
            </p>
            <p>
                {formatDate(planning_horizon[1], "date")}
              </p>
            </div>
          </div>

        </div>
        {/* <p> Created: {formatDate(created_at)} </p>  */}
        <p className="flex-1 flex justify-end items-end pr-3"> Last Modified: {formatDate(last_modified)} </p>
      </div>
    
      </Link>

      <div className="w-[5vw] min-w-20 flex gap-4 items-center justify-center border-l border-border mt-2 mb-2">
        
        <EditProjectDialog projectId={id} name={name} />
        
        <DeleteProjectDialog projectId={id} name={name}/>

      </div>
    </div>
  )
};