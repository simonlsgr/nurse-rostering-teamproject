import { projectCompilationEventsSubscribe } from "next/dist/build/swc/generated-native";
import Link from "next/link";

type ProjectCardProps = {
  id: number;
  name: string;
  nb_nurses: number;
};

function ProjectCard({ id, name, nb_nurses }: ProjectCardProps ) {

    return (
      <div 
        className="border rounded-xl w-full h-30 p-2 mb-4"
        key={id}
      >
        <Link 
            href={`/projects/${id}`}
            key={id}
            className="text-xl"
        >
          {name}
        </Link>
        
        <div className="pt-4">
          <p> ID: {id} </p> 
          <p> Nurses: {nb_nurses} </p>
        </div>
      
      </div>
    )
};

export default function ProjectsView(){
  
  const projects = [
    { id: 1, name: "Project A", num_of_nurses: 21 },
    { id: 2, name: "Project B", num_of_nurses: 32 },
  ];

  return (


    <div className="flex h-screen gap-2">
      
      {/* sidebar left*/}
      <div className="w-[10vw] min-w-[240px] max-w-[320px] hidden">
      </div>
      
      
      <div className="w-full">
      
        {/* topbar */}
        <div className="h-[2vw] min-h-[30px] max-h-[40px]">
        </div>
      
        {/* main view */}
        <div className="p-2">
      
          <h1 className="text-4xl font-bold pb-2 mb-4 border-b">
            Projects
          </h1>
      
          {/* projects list */}
          <div className="overflow-auto">
            {projects.map((project, idx) => (
                <ProjectCard key={idx} id={project.id} name={project.name} nb_nurses={project.num_of_nurses}/>
            ))}
          </div>
       
        </div>
      
      </div>

      {/* sidebar right */}
      <div className="w-[1vw]">
      </div>
    
    </div>
  );
}





