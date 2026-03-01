import { pollJob } from "@/app/api/solver";
import { fetchSolution } from "@/app/api/solution"
import { formatDate } from "@/lib/utils";
import { useJobs } from "@/store/solverStore";
import { Job } from "@/types/solverVars";
import { useSolutionsArray } from "@/store/solutionStore";
import { nanoid } from "nanoid";
import { uniqueNamesGenerator, Config, adjectives, animals } from 'unique-names-generator';

import RefreshIcon from '@mui/icons-material/Refresh';
import { SaveIcon } from "lucide-react";
import { useState } from "react";
import { Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, TextField } from "@mui/material";


type JobCardProps = {

  jobId: string;
  bgGray: boolean;
};


export default function JobCard({ jobId, bgGray }: JobCardProps) {

  const config: Config = {
    dictionaries: [adjectives, animals],
    separator: " ",
    style: "capital"
  }
  

  const addSolution = useSolutionsArray((s) => s.addSolution)

  const { jobs, updateJob, removeJob } = useJobs();
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const [saveOpen, setSaveOpen] = useState(false);
  const [solutionName, setSolutionName] = useState("");

  const handleOpenSave = () => {
    setSaveOpen(true);
  };

  const handleCloseSave = () => {
    setSaveOpen(false);
  };

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

  // TODO: save the solution in the backend
  const handleSaveSolution = async () => {
    setSaveOpen(false);
    try {
      const data = await fetchSolution(job.task_id);
      const name = solutionName || uniqueNamesGenerator(config);
      setSolutionName(name);
      addSolution({ solutionId: nanoid(), solution_name: name, solution: data.nurses_at_shifts });
      removeJob(job);

    } catch (err: any) {
      console.log(err.message);
      setError(err.message);
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
      <div className="flex">
        {job.status === "Completed" &&
        <div className={`h-10 w-10 flex items-center justify-center ${bgGray ? "hover:bg-white" : "hover:bg-gray-100"} rounded-lg transition duration-170`}>
          <SaveIcon onClick={handleOpenSave} />
        <Dialog open={saveOpen} onClose={handleCloseSave}>
        <DialogTitle>Save Solution</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Please enter a name for the solution.
          </DialogContentText>
            <TextField
              autoFocus
              margin="dense"
              id="name"
              name="name"
              label="Solution name"
              type="text"
              value={solutionName}
              fullWidth
              variant="standard"
              onChange={(event) => setSolutionName(event.target.value)}
            />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseSave}>Cancel</Button>
          <Button type="submit" onClick={handleSaveSolution}>
            Save
          </Button>
        </DialogActions>
        </Dialog>
        </div>

        }
        <div className={`h-10 w-10 flex items-center justify-center ${bgGray ? "hover:bg-white" : "hover:bg-gray-100"} rounded-lg transition duration-170`}>
          <RefreshIcon onClick={handleGetJob} />
        </div>

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
