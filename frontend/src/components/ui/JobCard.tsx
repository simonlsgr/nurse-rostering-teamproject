

type JobCardProps = {

  name: string
};


export default function JobCard({ name }: JobCardProps ){



  return (

    <div 
      className={`border-b border-l border-border rounded-lg rounded-tl-none w-[calc(100%-1rem)] h-18 p-2 pt-0 mb-2 mt-2 transition-all duration-170 ease-in-out`}
    >
      <div className="font-semibold text-xl"> 
        
        Title 

      </div>

      <div className="pt-1">

        Content

      </div>

    </div>
  );
}