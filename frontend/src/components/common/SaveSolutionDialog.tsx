import { useState } from "react";
import { Button } from "../ui/button";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "../ui/dialog";
import { fetchSolution } from "@/app/api/solution"
import { Input } from "../ui/input";
import { useJobs } from "@/store/solverStore";
import { useSolutionsArray } from "@/store/solutionStore";

import SaveIcon from '@mui/icons-material/Save';
import { uniqueNamesGenerator, Config, adjectives, animals } from 'unique-names-generator';
import { nanoid } from "nanoid";

type SaveSolutionDialogProps = {
    jobId: string;
    bgGray: boolean;
};


export default function SaveSolutionDialog({ jobId, bgGray }: SaveSolutionDialogProps) {

    const [openDialog, setOpenDialog] = useState<boolean>(false);
    const [solutionNameInput, setSolutionNameInput] = useState<string>("");
    const addSolution = useSolutionsArray((s) => s.addSolution)

    const config: Config = {
        dictionaries: [adjectives, animals],
        separator: " ",
        style: "capital"
    }

    const { jobs, updateJob, removeJob } = useJobs();
    const job = jobs[jobId];

    // TODO: save the solution in the backend
    const handleSaveSolution = async () => {
        try {
            const data = await fetchSolution(job.task_id);
            const name = solutionNameInput || uniqueNamesGenerator(config);
            setSolutionNameInput(name);
            addSolution({ solutionId: nanoid(), solution_name: name, solution: data.nurses_at_shifts });
            removeJob(job);

        } catch (err: any) {
            console.log(err.message);
        }
    }

    return (


        <Dialog open={openDialog} onOpenChange={setOpenDialog}>
            <DialogTrigger asChild>
                <div className={`h-10 w-10 flex items-center justify-center ${bgGray ? "hover:bg-white" : "hover:bg-gray-100"} rounded-lg transition duration-170`}>
                    <SaveIcon/>
                </div>

            </DialogTrigger>
            <DialogContent className="w-[calc(30vw)]">
                <DialogHeader>
                    <DialogTitle>Save Solution</DialogTitle>
                </DialogHeader>

                <Input
                placeholder="Name"
                value={solutionNameInput}
                onChange={(name) =>
                    setSolutionNameInput(() => ( name.target.value ))
                }
                />

                <DialogFooter className="mt-4">
                    <Button
                        variant="outline"
                        onClick={() => { setOpenDialog(false); }}
                    >
                        Cancel
                    </Button>
                    <Button variant={"default"} onClick={() => { handleSaveSolution(); setOpenDialog(false) }}>
                        Save
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>


    )
    
}