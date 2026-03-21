import { useState } from "react";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "../ui/dialog";
import { Button } from "../ui/button";
import ShiftList from "../rostering/ShiftList";
import { Shift } from "@/types/nurseVars";
import DynamicShiftList from "../rostering/DynamicShiftList";
import { useShifts } from "@/store/nurseStore";
import { editShift } from "@/app/api/shift";
import { useSelectedProject, useShiftTypes } from "@/store/projectStore";



export default function ViewShiftsDialog() {

  const [openDialog, setOpenDialog] = useState<boolean>(false);
  const [editShifts, setEditShifts] = useState<boolean>(false);

  const [demand, setDemand] = useState<number>(0);
  const [weightBelowDemand, setWeightBelowDemand] = useState<number>(0);
  const [weightAboveDemand, setWeightAboveDemand] = useState<number>(0);

  const [selectTypeChecked, setSelectTypeChecked] = useState(false);
  const [selectedType, setSelectedType] = useState("");

  const [selectedItems, setSelectedItems] = useState<Shift[]>([]);

  const { selectedProject } = useSelectedProject();
  const { shifts, updateShift } = useShifts();
  const { shiftTypes } = useShiftTypes();

  const handleSaveShiftParameters = () => {
    if(!selectedProject) return;

    selectedItems.forEach((shift) => {
      const editedShift = {...shift, demand: demand, weight_below_demand: weightBelowDemand, weight_above_demand: weightAboveDemand}; 
      
      editShift(editedShift, selectedProject.id);
      updateShift(editedShift);
    });

    setSelectedItems([]);
    setDemand(0); 
    setWeightBelowDemand(0); 
    setWeightAboveDemand(0);
    setEditShifts(false);
  }


  return (



    <Dialog open={openDialog} onOpenChange={setOpenDialog}>
      <DialogTrigger asChild>

        <Button className="bg-gray-50 rounded-none border-border" variant={"outline"}>
          View Shifts
        </Button>

      </DialogTrigger>
      <DialogContent className="!w-[48vw] !max-w-[1200px] h-[calc(80vh)]">
        <DialogHeader>
          <DialogTitle>View Shifts</DialogTitle>

            <div className="h-full flex gap-4 items-center bg-gray-50 rounded-2xl p-4">
              
              {!editShifts && (

                <Button 
                  className="border border-border rounded-none" 
                  variant={"outline"}
                  onClick={() => setEditShifts(true)}
                  >
                  Edit multiple shifts
                </Button>
              )}

              {editShifts && (

                <div className="flex gap-6 flex-1">

                  <div className="bg-white rounded-xl p-2 w-50 font-semibold flex items-center">
                    Speficy parameters to set for all selected shifts: 
                  </div>

                  <div className="bg-white rounded-xl p-2">
                    <div className="flex gap-2 items-center">
                      <p> Demand: </p>
                      <input
                        className="border border-border rounded-md p-1 w-10 ml-[73px] mb-1"
                        type="text"
                        inputMode="numeric"
                        value={demand}
                        onChange={(e) => {
                          const val = Number(e.target.value.replace(/\D/g, ""));
                          setDemand(val);
                        }}
                        />
                    </div>   
                      
                    <div className="flex gap-2 items-center">
                      <p> W. below demand: </p>
                      <input
                        className="border border-border rounded-md p-1 w-10 ml-[4.5px]"
                        type="text"
                        inputMode="numeric"
                        value={weightBelowDemand}
                        onChange={(e) => {
                          const val = Number(e.target.value.replace(/\D/g, ""));
                          setWeightBelowDemand(val);
                        }}
                        />
                    </div>
                    
                    <div className="flex gap-2 items-center">
                      <p> W. above demand: </p>
                      <input
                        className="border border-border rounded-md p-1 w-10 m-1"
                        type="text"
                        inputMode="numeric"
                        value={weightAboveDemand}
                        onChange={(e) => {
                          const val = Number(e.target.value.replace(/\D/g, ""));
                          setWeightAboveDemand(val);
                        }}
                        />
                    </div>         
                  </div>

                  <div className="bg-white rounded-xl p-2 w-50">
                    <p className="font-semibold"> Quick-Select: </p> 

                    <div className="flex flex-col gap-2 pl-2 pt-4">
                      <label className="flex items-center gap-2 select-none">
                        <input 
                          type="checkbox"
                          onChange={(e) => {
                            e.target.checked ? setSelectedItems(shifts) : setSelectedItems([]);
                          }}
                        />
                        <span>Select All</span>
                      </label>

                      <label className="flex items-center gap-2 select-none">
                        <input 
                          type="checkbox" 
                          checked={selectTypeChecked}
                          onChange={(e) => {
                            e.target.checked ? "" : setSelectedItems([])
                            setSelectTypeChecked(e.target.checked)
                          }}
                        />
                        <span>Select Type</span>

                        <select 
                          className="border border-gray-300 rounded-md p-1 disabled:opacity-50 w-15"
                          disabled={!selectTypeChecked}
                          value={selectedType}
                          onChange={(e) => {
                            setSelectedType(e.target.value);
                            setSelectedItems(shifts.filter((shift) => shift.type == e.target.value));
                          }}
                        >
                          <option value="">Type</option>

                          {shiftTypes.map((type) => (
                            <option key={type.id} value={type.name}>
                              {type.name}
                            </option>
                          ))}
                        </select>

                      </label>

                    </div>
                  </div>

                  <div className="flex gap-2 items-center justify-start flex-1">
                    <div className="border border-l h-full border-gray-100 mr-4"> </div>
                    <Button 
                      className="border border-border rounded-none" 
                      variant={"outline"}
                      onClick={() => { setSelectedItems([]); setDemand(0); setWeightBelowDemand(0); setWeightAboveDemand(0); setEditShifts(false);}}
                      >
                      Cancel
                    </Button>
                    <Button 
                      className="border border-border rounded-none" 
                      variant={"outline"}
                      onClick={() => {handleSaveShiftParameters(); setEditShifts(false)}}
                    >
                      Save
                    </Button>
                  </div>


                </div>

              )}

            </div>

        </DialogHeader>

        <div className="overflow auto">

          <div className="">

            <ShiftList 
              editShifts={editShifts} 
              setEditShifts={setEditShifts} 
              selectedItems={selectedItems}
              setSelectedItems={setSelectedItems}
            />

          </div>





        </div>

      </DialogContent>
    </Dialog>



  )

}