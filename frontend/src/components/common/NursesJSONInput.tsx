import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useState } from "react";
import { Nurse } from "@/types/nurseVars";
import { createNurse } from "@/app/api/nurse";
import { useSelectedProject, useShiftTypes } from "@/store/projectStore";
import { useNurses } from "@/store/nurseStore";
import { generateUID, validateNursesImport } from "@/lib/utils";
import MoreVertIcon from '@mui/icons-material/MoreVert';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger
} from "@/components/ui/dialog";


export default function NursesJSONInput() {
  const [openDialog, setOpenDialog] = useState(false);
  const [jsonInput, setJsonInput] = useState(nurseJsonTemplate);
  const [error, setError] = useState("");

  const { selectedProject } = useSelectedProject();
  const { nurses, setNurses } = useNurses();
  const { shiftTypes } = useShiftTypes();

  const formatJson = () => {
    try {
      const parsed = JSON.parse(jsonInput);
      setJsonInput(JSON.stringify(parsed, null, 2));
    } catch {}
  };

  const handleImport = async () => {
    if(!selectedProject) return;

    try {
      setError("");
  
      const parsed = JSON.parse(jsonInput);
  
      if (!Array.isArray(parsed)) {
        throw new Error("JSON must be an array");
      }
  
      parsed.forEach((nurse, index) => {
        if (!nurse.name || typeof nurse.uid !== "number") {
          throw new Error(`Invalid nurse at index ${index}`);
        }
      });
  
      const inputNurses: Nurse[] = parsed.map((n) => ({
        id: crypto.randomUUID(),
        uid: generateUID(),
        preferred_shifts: [],
        preferred_off_shifts: [],
        blocked_shifts: [],
        days_off: [],
        staff: true,
        min_time_between_shifts: "PT0S",
        preferred_shift_weight: {},
        preferred_off_shift_weight: {},
        minimum_work_time: 0,
        maximum_work_time: 0,
        minimum_consecutive_shifts: 0,
        maximum_consecutive_shifts: 0,
        minimum_consecutive_days_off: 0,
        maximum_weekends: 0,
        maximum_number_of_shifts_per_type: {},
        ...n,
      }));
  
      const validation = validateNursesImport(
        nurses,
        shiftTypes,
        selectedProject.planning_horizon
      );
  
      if (!validation.valid) {
        throw new Error(validation.error);
      }

      for (const nurse of inputNurses) {
        const res = await createNurse(nurse, selectedProject.id);
      }
      
      setNurses([...nurses, ...inputNurses])
      setJsonInput("");
    } catch (err: any) {
      setError(err.message || "Invalid JSON");
    }
  };

  return (
    <Dialog open={openDialog} onOpenChange={setOpenDialog}>
      <DialogTrigger>
        <div className="h-7 font-semibold rounded-none border-border border bg-background shadow-xs hover:bg-accent hover:text-accent-foreground dark:bg-input/30 dark:border-input dark:hover:bg-input/50 p-2 pt-1">
          Import via JSON
        </div>
      </DialogTrigger>
      <DialogContent className="!max-w-none w-[40vw] !max-h-none h-[85vh] overflow-auto">
        <DialogHeader>
          <DialogTitle>Import Nurses (JSON)</DialogTitle>
        </DialogHeader>

        <div className="flex flex-col gap-3">
          <Textarea
            value={jsonInput}
            onChange={(e) => setJsonInput(e.target.value)}
            className="min-h-[200px]  h-[68vh]"
          />

          {error && (
            <p className="text-red-500 text-sm">{error}</p>
          )}

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setOpenDialog(false)}>
              Cancel
            </Button>
        
            <Button 
              onClick={handleImport}
              disabled={!jsonInput.trim()}
            >
              Import
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>


  )
}

const nurseJsonTemplate = `[
  {
    "uid": 1,
    "name": "Anna",

    "preferred_shifts": [],
    "preferred_off_shifts": [],
    "blocked_shifts": [],

    "days_off": [],

    "preferred_shift_weight": {},
    "preferred_off_shift_weight": {},

    "minimum_work_time": 0,
    "maximum_work_time": 0,

    "minimum_consecutive_shifts": 0,
    "maximum_consecutive_shifts": 0,

    "minimum_consecutive_days_off": 0,

    "maximum_weekends": 0,

    "maximum_number_of_shifts_per_type": {
      "Early": 5,
      "Late": 5
    }
  }
]`;