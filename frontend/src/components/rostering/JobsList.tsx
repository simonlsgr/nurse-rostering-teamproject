import { useState } from "react";
import KeyboardArrowRightIcon from '@mui/icons-material/KeyboardArrowRight';
import JobCard from "../ui/JobCard";
import { Job } from "@/types/solverVars";
import { useJobs } from "@/store/solverStore";
import { motion, AnimatePresence } from "framer-motion";


export default function JobsList(){
  let grayCard = true;
  const { jobs } = useJobs();
  const jobValues = Object.values(jobs);

  const categories = ["active", "completed"];
  const runningJobs: Job[] = jobValues.filter((job) => job.status == "Submitted" || job.status == "Running")
  const finishedJobs: Job[] = jobValues.filter((job) => job.status == "Completed");
  const _jobs: Record<string, Job[]> = {"active": runningJobs, "completed": finishedJobs};

  const [openLists, setOpenLists] = useState<Record<string, boolean>>({});

  const toggleList = (category: string) => {
    setOpenLists((prev) => ({
      ...prev,
      [category]: !prev[category],
    }));
  };


  return (

    <div className="">

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
          transition-all duration-200 w-full border-b border-border overflow-auto
          ${isOpen ? "max-h-[38vh] opacity-100" : "max-h-0"}
          `}
          >


          {/* job cards here */}

          {_jobs[category].map((job: any) => {
            grayCard = !grayCard;

            return (
              <AnimatePresence key={job.task_id} mode="popLayout">
                <motion.div
                  key={job.task_id}
                  layout
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ duration: 0.17 }}
                  className="cursor-pointer select-none"
                >
                  <JobCard jobId={job.task_id} key={job.task_id} bgGray={grayCard}/>
                </motion.div>
              </AnimatePresence>
            )

          })}


        </div>
      </div>
      )})}

    </div>


  );
}
