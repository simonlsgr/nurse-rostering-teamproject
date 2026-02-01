import SidebarLeft from "@/components/layout/SidebarLeft";
import ProjectCard from "@/components/ui/ProjectCard";


export default function ProjectsView(){
  
  const projects = [
    { id: 1, name: "Project A", num_of_nurses: 21 },
    { id: 2, name: "Project B", num_of_nurses: 32 },
  ];

  return (


    <div className="flex h-screen gap-2">
      
      <SidebarLeft />
      
      
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





