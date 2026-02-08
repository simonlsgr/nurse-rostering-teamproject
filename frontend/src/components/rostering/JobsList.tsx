import { useState } from "react";
import { Button } from "@/components/ui/button";
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowRightIcon from '@mui/icons-material/KeyboardArrowRight';
import { motion } from "framer-motion";
import JobCard from "../ui/JobCard";


export default function JobsList(){

  const categories = ["active", "running"];

  const runningJobs = [
    { name: "job1" },
    { name: "job2 "},
  ];

  const finishedJobs = [
    { name: "job1" },
    { name: "job2 "},
  ];

  const jobs: Record<string, any> = {"active": runningJobs, "running": finishedJobs};


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
              
              <JobCard name={job.name} key={job.name}/>
            )

          })}


        </div>
      </div>
      )})}

    </div>


  );
}
