

type JobCardProps = {

  name: string
};


export default function JobCard({ name }: JobCardProps ){



  return (

    <div 
      className={`border-b border-l border-border rounded-lg rounded-tl-none w-[calc(100%-1rem)] h-16 p-2 pt-0 mb-2 mt-3 transition-all duration-130 hover:shadow-sm`}
    >
      <div className="font-semibold cursor-pointer max-w-[60px]"> 
        
        Title 

      </div>

      <div className="pt-1">

        Content

      </div>

    </div>
  );
}