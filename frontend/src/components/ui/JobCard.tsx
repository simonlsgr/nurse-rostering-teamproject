import { pollJob } from "@/app/api/solver";
import { formatDate } from "@/lib/utils";
import { useJobs } from "@/store/solverStore";
import { Job } from "@/types/solverVars";

import RefreshIcon from '@mui/icons-material/Refresh';
import { useState } from "react";


type JobCardProps = {

  jobId: string;
  bgGray: boolean;
};


export default function JobCard({ jobId, bgGray }: JobCardProps ){

  const { jobs, updateJob } = useJobs();
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const job = jobs[jobId];

  const handleGetJob = async () => {



    try {
      const data = await pollJob(job.task_id);
      updateJob(data);
      setError(null);
      setResult("Refresh successfull");
    } catch (err: any) {
      setError(err.message);
      setResult(null);

    }
  }

  return (

    <div 
      className={`cursor-pointer border-l border-border rounded-lg w-[calc(100%-1rem)] h-16 p-2 pt-0 mb-2 mt-3 transition-all duration-130 flex justify-between items-center ${bgGray ? "bg-gray-100 hover:shadow-sm" : "hover:shadow-xs"}`}
    >
      <div>
        <div className="font-semibold max-w-[60px]"> 

          {job.name}

        </div>

        <div className="pt-1 flex gap-4">

          Submitted @ {formatDate(job.submitted_at)} 
          <div className="border-l border-border "></div>

          Started @ {formatDate(jobs[jobId].started_at)} 
          <div className="border-l border-border "></div>

          Completed @ {formatDate(job.completed_at)} 


          <div className={`border-l border-border ${!error && !result ? "hidden" : ""}`}>
            {error && (
            <p className="text-red-600 pl-4">Error: {error}</p>
            )}
            {result && (
              <p className="text-green-600 pl-4">{result}</p>
            )}

          </div>
          

        </div>
      </div>

      <div className="h-10 w-10 flex items-center justify-center hover:bg-gray-100 rounded-lg transition duration-170">  
          <RefreshIcon onClick={handleGetJob}> </RefreshIcon>          
      </div>

    </div>
  );
}

/* 
{(Object.keys(job) as (keyof typeof job)[]).map((key) => {

  return (
    <div key={key} >
      {job[key]}
    </div>
  )

})}
 */