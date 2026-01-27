import { projectCompilationEventsSubscribe } from "next/dist/build/swc/generated-native";
import Link from "next/link";


export default function ProjectsView(){
  
  const projects = [
    { id: 1, name: "Projekt A" },
    { id: 2, name: "Projekt B" },
  ];

  return (
    <div>
      {projects.map((project) => (
        <Link 
          href={`/projects/${project.id}`}
          key={project.id}
        >
          {project.name}
        </Link>

      ))}



    </div>
  );
}