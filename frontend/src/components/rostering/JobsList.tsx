import { useState } from "react";
import KeyboardArrowRightIcon from '@mui/icons-material/KeyboardArrowRight';
import JobCard from "../ui/JobCard";
import { Job } from "@/types/solverVars";
import { pollJob } from "@/app/api/solver";


export default function JobsList(){



  const categories = ["active", "running"];

  const runningJobs: Job[] = [
    { name: "job1",
      task_id: "9814d6a3-534b-40d3-b6bd-d45df0802e78",
      status: "Submitted",
      submitted_at: "2026-02-13T17:29:28.670131",
      started_at: null,
      completed_at: null,
      error: null
    },
    { name: "job2",
      task_id: "9814d6a3-534b-40d3-b6bd-d45df0802e79",
      status: "Submitted",
      submitted_at: "2026-02-13T17:29:28.670132",
      started_at: null,
      completed_at: null,
      error: null
    },
  ];

  const finishedJobs: Job[] = [];

  const jobs: Record<string, Job[]> = {"active": runningJobs, "running": finishedJobs};


  const [openLists, setOpenLists] = useState<Record<string, boolean>>({});

  const toggleList = (category: string) => {
    setOpenLists((prev) => ({
      ...prev,
      [category]: !prev[category],
    }));
  };


  return (

    <div>

      {categories.map((category) => {

        const isOpen = openLists[category];

        return (
        
        <div className="relative mb-4 pb-2" key={category}>

        <button
        onClick={() => toggleList(category)}
        className="w-full text-left capitalize cursor-pointer border-b border-border"
        >
          {/* wrap in div for animation to work */}
          <div className={`inline-block transition-transform duration-100 ease-in-out ${isOpen ? "rotate-90" : ""}`}>
            <KeyboardArrowRightIcon className={`p-1 pb-2`}/>
          </div>
        {" " + category}
        </button>

        <div
        className={`
          left-0 mt-1
          transition-all duration-300 w-full
          ${isOpen ? "max-h-60 opacity-100" : "max-h-0"}
          overflow-hidden
          `}
          >


          {/* job cards here */}

          {jobs[category].map((job: any) => {

            return (
              
              <JobCard job={job} key={job.name}/>
            )

          })}


        </div>
      </div>
      )})}

    </div>


  );
}
