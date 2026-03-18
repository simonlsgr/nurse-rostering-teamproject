import { useEffect, useState } from "react";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "../ui/dialog";
import { Button } from "../ui/button";
import AddIcon from '@mui/icons-material/Add';
import { Nurse, Shift } from "@/types/nurseVars";
import { createDefaultNurse, formatDate } from "@/lib/utils";
import { capitalize, Switch, Tooltip } from "@mui/material";
import DynamicShiftList from "../rostering/DynamicShiftList";
import { useInstance } from "@/store/instanceStore";
import { Calendar } from "@/components/ui/calendar";
import { useHandleCreateNurse } from "@/hooks/nurseHooks";
import { useNewNurse } from "@/store/nurseStore";


export default function CreateNurseDialog() {

  const [openDialog, setOpenDialog] = useState<boolean>(false);
  const [selectedPreferredShifts, setSelectedPreferredShifts] = useState<Shift[]>([]);
  const [selectedPreferredOffShifts, setSelectedPreferredOffShifts] = useState<Shift[]>([]);
  const [dates, setDates] = useState<Date[] | undefined>([]);

  const { newNurse, setNewNurse } = useNewNurse();
  const { handleCreateNurse } = useHandleCreateNurse();

  
  const { shifts } = useInstance();

  useEffect(() => {
    if (dates) {
      setNewNurse(prev => ({
        ...prev,
        "days_off": dates?.map((date) => date.toISOString().split("T")[0])
      })); 
    }

    setNewNurse(prev => ({
      ...prev,
      "preferred_shifts": selectedPreferredShifts.map((s) => s.uid),
      "preferred_off_shifts": selectedPreferredOffShifts.map((s) => s.uid),

    })); 



   }, [dates, selectedPreferredShifts, selectedPreferredOffShifts])


   useEffect(() => {
    setSelectedPreferredShifts([]);
    setSelectedPreferredOffShifts([]);
    setDates([]);
  }, [openDialog])

  
  const dynamicAttributeDisplay = (key: string) => {
    
    // these attributes are currently not needed
/*     if (key == "staff") {
      return (
        <div className="flex gap-2 items-center">
          <Switch
            checked={newNurse.staff}
            onChange={(event, newChecked) => {
              setNewNurse({...newNurse, "staff": !newNurse.staff});
            }}
            />
          <p> {newNurse.staff ? "true" : "false"} </p>
        </div>

      )
    }

    if (key == "min_time_between_shifts") {
      return (
        <Textarea
          className="mb-2 min-h-none"     
          value={newNurse[key]}
          onChange={(e) => {
            setNewNurse({...newNurse, [key]: e.target.value})
          }}     
        />
      )
    } */

    if (key == "maximum_number_of_shifts_per_type") {
      return (
        <div className="pb-1">

          {/* if we allow more shift types, change this to the state that handles this */}
          {Object.keys({"E": 0, "L": 0}).map((type) => (

            <div 
              key={type}
              className="flex gap-1 items-center"
            >
              <p className="mb-2"> {type}: </p>
              <input
                className="border border-border rounded-md p-1 mb-2"
                type="text"
                inputMode="numeric"
                value={newNurse[key][type]}
                onChange={(e) => {
                  const val = Number(e.target.value.replace(/\D/g, ""));
                  setNewNurse(prev => ({
                    ...prev,
                    [key]: {
                      ...(prev[key as keyof Nurse] as Record<string, number>),
                      [type]: val
                    }
                  }));
                }}
              />
            </div>

          ))}
      
      </div>
      )
    }

    return (
      <input
        className="border border-border rounded-md p-1 mb-2"
        type="text"
        inputMode="numeric"
        value={newNurse[key as keyof Nurse] as any}
        onChange={(e) => {
          const val = Number(e.target.value.replace(/\D/g, ""));
          setNewNurse({...newNurse, [key]: val});
        }}
      />
    )
  }

  const setPreferredShiftWeight = (weight: number, shift: Shift, unset?: boolean) => {

    if (unset) {
      const {[shift.uid]: foo, ...rest} = newNurse.preferred_shift_weight;
      setNewNurse(prev => ({
        ...prev,
        preferred_shift_weight: rest
      }));

    } else {
      setNewNurse(prev => ({
        ...prev,
        preferred_shift_weight: {
          ...newNurse.preferred_shift_weight,
          [shift.uid]: weight
        }
      }));
    }
  }

  const setPreferredOffShiftWeight = (weight: number, shift: Shift, unset?: boolean) => {

    if (unset) {
      const {[shift.uid]: foo, ...rest} = newNurse.preferred_off_shift_weight;
      setNewNurse(prev => ({
        ...prev,
        preferred_off_shift_weight: rest
      }));

    } else {
      setNewNurse(prev => ({
        ...prev,
        preferred_off_shift_weight: {
          ...newNurse.preferred_off_shift_weight,
          [shift.uid]: weight
        }
      }));
    }
  }


  return (

    <Dialog open={openDialog} onOpenChange={setOpenDialog}>
      <DialogTrigger asChild>
        
      <AddIcon
        fontSize="small"
        className="hover:bg-gray-200 rounded text-muted-foreground"
      />

      </DialogTrigger>
      <DialogContent className="!w-[48vw] !max-w-[1200px] h-[calc(80vh)]">
        <DialogHeader>
          <DialogTitle>Create a new nurse</DialogTitle>
        </DialogHeader>

        <div className="overflow-auto">


        <div className="mb-5">
          <div className="flex gap-3 group"> 
            <p className="font-semibold mb-2" key={`title-name`}>
              {capitalize("name")}:
            </p>              
          </div>

          <div className={`border-b border-border w-full pl-1 overflow-auto`} key={`content-name`}>
            <input
              className="border border-border rounded-md p-1 mb-2"
              value={newNurse.name}
              onChange={(e) =>
                setNewNurse((n: any) => ({ ...n, name: e.target.value }))
              }
            />
          </div>  
        </div>

        <div className="flex gap-4 mb-2 border-b border-border pb-3">
          <div key={"preferred_shifts"} className={`mb-2 overflow-auto max-h-[calc(40vh)] ${newNurse.preferred_shifts.length >= 1 ?"h-[calc(40vh)]" : "h-min"} w-[calc(20vw)] max-w-100 border border-border rounded-3xl p-2 pr-0 bg-gray-50 shadow-xs`}>

            <h2 className="pb-2 pl-2 font-semibold"> Preferred Shifts: </h2>
            <DynamicShiftList 
              shifts={shifts.filter((s) => !selectedPreferredOffShifts.includes(s))} 
              shift_weights={newNurse.preferred_shift_weight}
              setShiftWeight={setPreferredShiftWeight}
              selectable={true} 
              selectedItems={selectedPreferredShifts} 
              setSelectedItems={setSelectedPreferredShifts} 
            />

          </div>

          <div key={"preferred_off_shifts"} className={`mb-2 overflow-auto max-h-[calc(40vh)] ${newNurse.preferred_off_shifts.length >= 1 ?"h-[calc(40vh)]" : "h-min"} w-[calc(20vw)] max-w-100 border border-border rounded-3xl p-2 pr-0 bg-gray-50 shadow-xs`}>

            <h2 className="pb-2 pl-2 font-semibold"> Preferred Off-Shifts: </h2>
            <DynamicShiftList 
              shifts={shifts.filter((s) => !selectedPreferredShifts.includes(s))} 
              shift_weights={newNurse.preferred_off_shift_weight}
              setShiftWeight={setPreferredOffShiftWeight}
              selectable={true}
              selectedItems={selectedPreferredOffShifts} 
              setSelectedItems={setSelectedPreferredOffShifts} 
              />

          </div>
          
        </div>

        <div className={`border-b border-border w-full pl-1 mb-2 overflow-auto`}>
          <p className="font-semibold mb-2"> Days Off: </p>
            <Calendar
            mode="multiple"
            selected={dates}
            onSelect={setDates}
            hidden={{
              before: new Date("2018-01-01"), 
              after: new Date("2018-01-14")
            }}
            startMonth={ new Date(2018, 0) }
            endMonth={ new Date(2018, 0) }
            defaultMonth={ new Date("2018-01-01") }
          />
        </div>


        {Object.keys(newNurse)
        .filter((keyy) => !["id", "db_id", "uid", "name", "preferred_shifts", "preferred_off_shifts", "blocked_shifts", "preferred_shift_weight", "days_off", "preferred_off_shift_weight", "staff", "min_time_between_shifts"].includes(keyy))
        .map((key) => 
          <div key={key} className="mb-2">

            <div className="flex gap-3 group"> 
              <p className="font-semibold mb-2" key={`title-${key}`}>
                {capitalize(key.replaceAll("_", " "))}:
              </p>

              
            </div>

            <div className={`border-b border-border w-full pl-1 overflow-auto`} key={`content-${key}`}>

                <div>
                  {dynamicAttributeDisplay(key)}
                  {/* {key == "maximum_number_of_shifts_per_type" ? displayMaximumShiftsPerType() : JSON.stringify(newNurse[key as keyof Nurse])} */}
                </div>


            </div>  
          </div>
        )}
        </div>





        <DialogFooter className="mt-4 flex items-end">
          <Button
            variant="outline"
            onClick={() => {
              setOpenDialog(false); 
              setNewNurse(createDefaultNurse());
            }}
          >
            Cancel
          </Button>
          <Button 
            onClick={() => {
              setOpenDialog(false);
              handleCreateNurse();
              }}
            >
            Create
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    
  )
}