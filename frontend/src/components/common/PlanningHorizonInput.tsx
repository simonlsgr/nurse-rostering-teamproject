import { useNewProject } from "@/store/projectStore";
import { useEffect, useState } from "react";


export default function PlanningHorizonInput(){

  const [startDate, setStartDate] = useState<string>("");
  const [endDate, setEndDate] = useState<string>("");

  const { setNewProject } = useNewProject();


  useEffect(() => {
    if (startDate && endDate && endDate < startDate) {
      alert("End date cannot be before start date");
      return;
    }

    setNewProject(prev => ({
      ...prev,
      planning_horizon: [startDate, endDate]
    }));

  }, [startDate, endDate]);

  return (
    <div>

      <p className="font-semibold mb-2"> Specify planning horizon: </p>
      <div className="pl-10">
      
        <div className="flex gap-2 items-center mb-2">
          <p className="w-10"> Start: </p>      
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="border border-border p-2 rounded"
            />
        </div>
       
        <div className="flex gap-2 items-center">
          <p className="w-10"> End: </p>
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            min={startDate}
            className="border p-2 border-border rounded"
          />
        </div>
      
      </div>
    </div>

  )
}