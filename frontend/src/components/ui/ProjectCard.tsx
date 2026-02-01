import Link from "next/link";


type ProjectCardProps = {
  id: number;
  name: string;
  nb_nurses: number;
};

export default function ProjectCard({ id, name, nb_nurses }: ProjectCardProps ) {

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