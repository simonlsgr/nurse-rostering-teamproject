import { createProject } from "@/app/api/project";
import { Button } from "@/components/ui/button";
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { createDefaultNewProject, generateDatesFromPlanningHorizon } from "@/lib/utils";
import { useNewProject, useProjects } from "@/store/projectStore";
import { NewProject, Project, ShiftType } from "@/types/projectVars";
import { capitalize } from "@mui/material";
import { useEffect, useState } from "react";
import PlanningHorizonInput from "./PlanningHorizonInput";
import ShiftTypesInput from "./ShiftTypesInput";
import NotFollowedByShiftTypesInput from "./NotFollowedByShiftTypesInput";
import { createShiftType } from "@/app/api/shiftType";
import { useGenerateShifts } from "@/hooks/nurseHooks";
import { createShift, createShifts } from "@/app/api/shift";
import ProjectJSONInput from "./ProjectJSONInput";
import { Shift } from "@/types/nurseVars";
import { createNurse } from "@/app/api/nurse";



export default function CreateProjectDialog(){

  const [openDialog, setOpenDialog] = useState<boolean>(false);
  const [inputJson, setInputJson] = useState<boolean>(false);

  const [jsonInput, setJsonInput] = useState(projectJsonTemplate);

  const { newProject, setNewProject } = useNewProject();
  const { updateProject } = useProjects();
  const { generateShifts } = useGenerateShifts();

  useEffect(() => {
    
    setNewProject(createDefaultNewProject());

  }, [openDialog])


  
  const formatJson = (input: string) => {
    try {
      const parsed = JSON.parse(input);
      return JSON.stringify(parsed, null, 2);
    } catch {
      return null; 
    }
  };

  function calculateDuration(startISO: string, endISO: string): string {
    const start = new Date(startISO);
    const end = new Date(endISO);
  
    let diff = (end.getTime() - start.getTime()) / 1000; // Sekunden
  
    // falls Schicht über Mitternacht geht
    if (diff < 0) {
      diff += 24 * 60 * 60;
    }
  
    const hours = Math.floor(diff / 3600)
      .toString()
      .padStart(2, "0");
  
    const minutes = Math.floor((diff % 3600) / 60)
      .toString()
      .padStart(2, "0");
  
    return `${hours}:${minutes}:00`;
  }

  function formatTime(iso: string): string {
    const d = new Date(iso);
  
    return d.toLocaleTimeString("de-DE", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  }

  function deriveShiftTypes(shifts: Shift[]): ShiftType[] {
    const map = new Map<string, Shift>();
  
    shifts.forEach((shift) => {
      if (!map.has(shift.type)) {
        map.set(shift.type, shift);
      }
    });
  
    return Array.from(map.entries()).map(([type, shift]) => ({
      id: crypto.randomUUID(),
      name: type,
      start: formatTime(shift.start_time),
      end: formatTime(shift.end_time),
      duration: calculateDuration(shift.start_time, shift.end_time),
      not_followed_by_shift_types:
        shift.not_followed_by_shift_types ?? [],
    }));
  }

  const handleImport = async () => {

    try {
  
      const formatted = formatJson(jsonInput);

      if (!formatted) {
        throw new Error("Invalid JSON input");
      }
      
      const parsed = JSON.parse(formatted);  
      const inputNurses = parsed["nurses"];
      const inputShifts = parsed["shifts"];
      const inputName = parsed["name"];
      const shiftTypes = deriveShiftTypes(inputShifts);
      const planningHorizon: [string, string] = [inputShifts[0].start_time.split("T")[0], inputShifts[inputShifts.length-1].end_time.split("T")[0]];


      console.log(inputNurses);
      console.log(inputShifts);
      console.log(inputName);
      console.log(shiftTypes);
      console.log(planningHorizon);

      console.log({"name": inputName, "planning_horizon": planningHorizon, "shift_types": shiftTypes, "id": crypto.randomUUID()});

      const projectId = crypto.randomUUID();
      const currentProject = {"name": inputName, "planning_horizon": planningHorizon, "shift_types": shiftTypes, "id": projectId};

      setNewProject(prev => ({...prev, ...currentProject}))

      const project = await handleCreateProject(currentProject, inputShifts);
      if (!project){
        alert("Project creation failed");
        return;
      }
    
      for (const nurse of inputNurses){
        const res = await createNurse({id: crypto.randomUUID(), ... nurse}, project.id);
      }

      setJsonInput("");
    } catch (err: any) {
      alert(err.message || "Invalid JSON");
    }
  };


  const handleCreateProject = async (project?: NewProject, inputShifts?: Shift[]) => {
    if (!newProject) return;
    
    const currentProject = project ?? newProject;

    const horizon = currentProject.planning_horizon ?? ["",""];
    const startDate = horizon[0];
    const endDate = horizon[1];
    
    if (startDate && endDate &&  endDate.length == startDate.length && endDate < startDate) {
      alert("End date cannot be before start date");
      return;
    }


    try {

      const { shift_types, ...project } = currentProject;

      const project_res: Project = await createProject(project as Project);
      updateProject(project_res);

      if (shift_types) {

        for(const shift_type of shift_types) {
          const res = await createShiftType(shift_type, project_res.id);
          if (!res.id) {
            alert(`Failed to create shift type ${shift_type.name}`);
          }
        }
        
      }

      if (!inputJson) {

        const newShifts = generateShifts(generateDatesFromPlanningHorizon(project_res.planning_horizon), shift_types ?? []);
        const res = await createShifts(newShifts, project_res.id);
        if (!res) {
          alert(`Failed to create shifts`);
        }
      } else if (inputShifts) {

        const res = createShifts(inputShifts.map((shift) => ({...shift, id: crypto.randomUUID()})), project_res.id)



      }

      return project_res;

      /* 
      for (const shift of newShifts) {
        const res = await createShift(shift, project_res.id);
        if (!res.id) {
          alert(`Failed to create shift ${shift.name}`);
        }
      }
 */
    }
    catch (err: any) {
      alert("Creation failed");
    }


  }

  return (
    <Dialog open={openDialog} onOpenChange={setOpenDialog}>
    <DialogTrigger asChild>
      
      <Button
        className="rounded-4xl m-4 h-15 text-xl"
      >
        New project
      </Button>

    </DialogTrigger>
    <DialogContent className="!max-w-none w-[48vw] h-[80vh] bg-gray-100">
      <DialogHeader className="h-min">
        <DialogTitle>
          Create a new project
        </DialogTitle>
        <div className="flex justify-end">

        {!inputJson && (
          <Button 
          variant={"outline"}
          className="border-border rounded-none h-7 w-min mr-2"
          onClick={() => setInputJson(true)}
          >
              Use JSON
            </Button>
          )}

          {inputJson && (
            <Button 
            variant={"outline"}
            onClick={() => setInputJson(false)}
            className="border-border rounded-none h-7 w-min mr-2"
            >
              Use Interface
            </Button>
          )}
          </div>
      </DialogHeader>

      {!inputJson && (

      <div className="overflow-auto flex flex-col gap-4 pr-2">
        <div className="rounded-2xl bg-white p-3">
          <p className="font-semibold mb-2"> Name: </p>
            <div className="">
              <input
                className="border border-border rounded-md p-1 mb-2"
                value={newProject.name}
                onChange={(e) =>
                 setNewProject(prev => ({...prev, "name": e.target.value}))
                }
                />
          </div>
        </div>
        
        <div className="rounded-2xl bg-white p-3">
          <PlanningHorizonInput />
        </div>
      
        <div className="rounded-2xl bg-white p-3">
          <ShiftTypesInput />
        </div>

        <div className="rounded-2xl bg-white p-3">
          <NotFollowedByShiftTypesInput />
        </div>

      </div>
      )}

      {inputJson && (

        <ProjectJSONInput 
          jsonInput={jsonInput}
          setJsonInput={setJsonInput}
        />

      )}

      {JSON.stringify(newProject.planning_horizon)}
      <DialogFooter className="mt-4 flex items-end">
        <Button
          variant="outline"
          onClick={() => {setOpenDialog(false); setNewProject(createDefaultNewProject())}}
        >
          Cancel
        </Button>
        <Button onClick={() => {(inputJson ? handleImport() : handleCreateProject()); setOpenDialog(false); setNewProject(createDefaultNewProject())}}>
          Create
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
  )
}


const projectJsonTemplate = `{

  "name": "",
  "nurses": [

    ],
  "shifts: [
  
    ],
}`;