'use client';



import { Instance, Shift, Nurse, Solution } from "@/types/nurseVars";
import { useInstance } from "@/store/instanceStore";
import { useSolution } from "@/store/solutionStore";
import { use, useEffect, useMemo, useState } from "react";
import { 
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { Tooltip } from "@mui/material"
import React from "react";





// interface Nurse {
//   uid: number;
//   name: string;
//   preferred_shifts: number[];
//   preferred_off_shifts: number[];
//   blocked_shifts: number[];
//   days_off: string[];
//   staff: boolean;
//   min_time_between_shifts: string;
//   preferred_shift_weight: Record<string, number>;
//   preferred_off_shift_weight: Record<string, number>;
//   minimum_work_time: number;
//   maximum_work_time: number;
//   minimum_consecutive_shifts: number;
//   maximum_consecutive_shifts: number;
//   minimum_consecutive_days_off: number;
//   maximum_weekends: number;
//   maximum_number_of_shifts_per_type: Record<string, number>;
// }

// interface Shift {
//   uid: number;
//   name: string;
//   start_time: string;
//   end_time: string;
//   demand: number;
//   type: string;
//   not_followed_by_shift_types: string[];
//   weight_below_demand: number;
//   weight_above_demand: number;
// }


// interface Instance {
//   nurses: Nurse[];
//   shifts: Shift[];
//   staff_weight: number;
// }

interface Consecutives {
  count: number;
  on: boolean;
  startDate: string;
}

type InfeasibilityReasonByDate = Record<string, Set<string>>;
type shiftUid = number;
type InfeasibilityDetails = Record<shiftUid, InfeasibilityReasonByDate>;





function NurseTableHeader({table}: {table: ReturnType<typeof useReactTable>}) {
  return (
    <thead className="bg-gray-200">
      {table.getHeaderGroups().map(hg => (
        <tr key={hg.id} className="position-sticky top-0 ">
          {hg.headers.map(h => (
            <th key={h.id} className="outline px-4 py-2 sticky top-0 first:z-1 first:left-0  bg-gray-200">
              {flexRender(h.column.columnDef.header, h.getContext())}
            </th>
          ))}
        </tr>
      ))}
    </thead>
  );
  
}

function NurseTableBody({
  table, 
  setTableData,
  shift_types,
  instance,
  hoveredColumn,
  setHoveredColumn,
  infeasibilityDetails
}:{
  table: ReturnType<typeof useReactTable>, 
  setTableData: React.Dispatch<React.SetStateAction<any[]>>, 
  shift_types: {value: string, label: string}[], 
  instance: Instance, 
  hoveredColumn: string | null, 
  setHoveredColumn: React.Dispatch<React.SetStateAction<string | null>>,
  infeasibilityDetails: InfeasibilityDetails
}) {
  return (
  <tbody>
    {table.getRowModel().rows.map(row => (
      <tr key={row.id} className="group box-border">
        {row.getVisibleCells().map(cell => {
          const date = cell.column.id;
          const isNurseColumn = date === "nid";
          const cellValue = String(cell.getValue() ?? "");
          const selectedShift = cellValue === "None" ? "empty" : cellValue;
          
          const nurseUid = String((row.original as any)?.Nurse ?? "");
          const cellInfeasibility = infeasibilityDetails[Number(nurseUid)]?.[date];
          const cellInfeasibilityNode = (<div>
            {[...(cellInfeasibility ?? new Set<String>())].map((reason, index, arr) => {
              return (
                <React.Fragment key={reason}>
                {reason}
                {index < arr.length - 1 && <br />}
              </React.Fragment>
              );
            })
            }
          </div>);

          
          
          const hasInfeasibility = cellInfeasibility && cellInfeasibility.size > 0;
          return (
            <Tooltip key={cell.id} title={hasInfeasibility ? cellInfeasibilityNode : ""} placement="top" arrow disableInteractive>
            <td 
            key={cell.id} 
            className={`w-min h-min px-4 py-2 box-border group-hover:border-y-2 hover:bg-gray-400! first:sticky first:outline-1 first:outline-gray-200 left-0 ${hasInfeasibility ? "bg-red-600!" : "bg-white"} ${hoveredColumn == cell.column.id ? "border-x-2" : ""}`}
            onMouseEnter={() => setHoveredColumn(date)}
            onMouseLeave={() => setHoveredColumn(null)}
            >
              {isNurseColumn ? (
                getNurseByUid(instance, Number(nurseUid))?.name || "Unknown Nurse"
              ) : (
                <select
                  name={`shift-${nurseUid}-${date}`}
                  value={selectedShift}
                  onChange={(e) => {
                    const nextShift = e.target.value === "empty" ? "None" : e.target.value;
                    setTableData((prev) => {
                      const updated = prev.map((entry, index) => {
                        if (index !== row.index) return entry;
                        return { ...entry, [date]: nextShift };
                      });
                      return updated;
                    });
                  }}
                  className="p-2 w-full box-border border-2 border-transparent hover:border-blue-500! focus:border-blue-500! focus:outline-none"
                >
                  {shift_types.map((type) => (
                    <option key={type.value} value={type.value} disabled={getNurseByUid(instance, Number(nurseUid))?.days_off.includes(date) ? true : false}>
                      {type.label}
                    </option>
                  ))}
                </select>
              )}
            </td>
            </Tooltip>
          );
        })}
      </tr>
    ))}
  </tbody>
  );
}

function getDatesFromTableData(tableData: any[]) {
  if (tableData.length === 0) return [];
  return Object.keys(tableData[0]).filter(key => key !== "Nurse");
}

function getShiftTypes(instance: Instance) {
  const uniqueTypes = new Set<string>();
  uniqueTypes.add("");
  instance.shifts.forEach((shift: any) => {
    uniqueTypes.add(shift.type);
  });
  return Array.from(uniqueTypes).map(type => ({
    value: type === "" ? "" : type,
    label: type === "" ? "" : type,
  }));
  
}

function NurseTable({tableData, setTableData, instance, infeasibilityDetails}:{tableData: any[], setTableData: React.Dispatch<React.SetStateAction<any[]>>, instance: Instance, infeasibilityDetails: InfeasibilityDetails}) {

  console.log("Rendering NurseTable with data:", tableData);
  const dates = getDatesFromTableData(tableData);

  const shift_types = getShiftTypes(instance);

  const [hoveredColumn, setHoveredColumn] = useState<string | null>(null);

  const columns = useMemo(() => [
    {
      header: "Nurse",
      accessorKey: "nid",
    },
    ...dates.map((date) => ({
      header: date,
      accessorKey: date,
    })),
  ],
  [dates]);

  const table = useReactTable({
    data: tableData,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });



  return (
    <div className="overflow-x-auto max-h-[40vh]">
      <table className="border-border border overflow-x-hidden">
        <NurseTableHeader table={table} />
        <NurseTableBody table={table} setTableData={setTableData} shift_types={shift_types} instance={instance} hoveredColumn={hoveredColumn} setHoveredColumn={setHoveredColumn} infeasibilityDetails={infeasibilityDetails}/>
      </table>
    </div>
  );
}


function getNurseByUid(instance: Instance, uid: number) {
  return instance.nurses.find((nurse) => nurse.uid === uid);
}

function instanceSolutionToTableData({instance, solution}: { instance: Instance, solution: Solution}) {
  
  const dates = instance.shifts.map((shift) =>
    shift.start_time.split("T")[0]
  );
  
  const nurses = instance.nurses.map((nurse) => nurse.name);

  const nurseAtDates = instance.nurses.map(
    (nurse) => {
      const nurseSchedule: Record<string, string> = {"Nurse": nurse.uid.toString()};
      
      dates.forEach((date) => {
        let shiftType = "";

        instance.shifts.forEach((shift) => {
          
          if (shift.start_time.split("T")[0] === date) {

            const assignedNurses = solution[shift.uid] || [];
            if (assignedNurses.includes(nurse.uid)) {
              shiftType = shift.type;
            } else {
            } 
          }
        });
        nurseSchedule[date] = shiftType;
      });
      return nurseSchedule;
    }
  );
  
  

  return nurseAtDates; 
}

function getShiftByUid({instance, shiftuid}: {instance: Instance, shiftuid: number}) {
  return instance.shifts.find((shift) => { shift.uid === shiftuid});
}

function getShiftDate(shift: Shift) {
  return shift.start_time.split("T")[0];
}


function getFirstDateOfInstance(instance: Instance) {
  if (instance.shifts.length === 0) return null;
  const dates = instance.shifts.map((shift) => shift.start_time.split("T")[0]);
  return dates.reduce((minDate, currentDate) => currentDate < minDate ? currentDate : minDate);
}

function getLastDateOfInstance(instance: Instance) {
  if (instance.shifts.length === 0) return null;
  const dates = instance.shifts.map((shift) => shift.start_time.split("T")[0]);
  return dates.reduce((maxDate, currentDate) => currentDate > maxDate ? currentDate : maxDate);
}


// Helper for calculating consecutive shifts and days off for a nurse, used in feasibility checks
function getConsecutivesArrayForNurse({instance, solution, nurseUid}: {instance: Instance, solution: Solution, nurseUid: number}) {
  const shiftsByDate: Record<string, shiftUid[]> = {};

  const consecutiveShifts: Consecutives[] = [];
  instance.shifts.forEach((shift) => {
    const shiftDate = getShiftDate(shift);
    if (!shiftsByDate[shiftDate]) {
      shiftsByDate[shiftDate] = [];
    }
    shiftsByDate[shiftDate].push(shift.uid);
  });
  
  const checkedDates = new Set<string>();
  Object.keys(shiftsByDate).forEach((date) => {
    if (checkedDates.has(date)) return;
    const shiftUids = shiftsByDate[date];
    const isAssigned = shiftUids.some(shiftUid => {
      const assignedNurses = solution[shiftUid] || [];
      return assignedNurses.includes(nurseUid);
    });
    
    if (isAssigned) {
      let consecutiveCount = 1;
      let nextDate = new Date(new Date(date).getTime() + (24 * 60 * 60 * 1000)).toISOString().split("T")[0];
      while (shiftsByDate[nextDate]) {
        const nextShiftUids = shiftsByDate[nextDate];
        const nextIsAssigned = nextShiftUids.some(shiftUid => {
          const assignedNurses = solution[shiftUid] || [];
          return assignedNurses.includes(nurseUid);
        });
        if (nextIsAssigned) {
          consecutiveCount++;
          checkedDates.add(nextDate);
          nextDate = new Date(new Date(nextDate).getTime() + (24 * 60 * 60 * 1000)).toISOString().split("T")[0];
        } else {
          break;
        }
      }
      consecutiveShifts.push({
        count: consecutiveCount,
        on: true,
        startDate: date,
      });
    } else {
      let consecutiveCount = 1;
      let nextDate = new Date(new Date(date).getTime() + (24 * 60 * 60 * 1000)).toISOString().split("T")[0];
      while (shiftsByDate[nextDate]) {
        const nextShiftUids = shiftsByDate[nextDate];
        const nextIsNotAssigend = nextShiftUids.every(shiftUid => {
          const assignedNurses = solution[shiftUid] || [];
          return !assignedNurses.includes(nurseUid);
        });
        if (nextIsNotAssigend) {
          consecutiveCount++;
          checkedDates.add(nextDate);
          nextDate = new Date(new Date(nextDate).getTime() + (24 * 60 * 60 * 1000)).toISOString().split("T")[0];
        } else {
          break;
        }
      }
      consecutiveShifts.push({
        count: consecutiveCount,
        on: false,
        startDate: date,
      });
    }
  });
  return consecutiveShifts;
  
}

export function MainView(){
  
  const nurses = useInstance((s) => s.nurses);
  const shifts = useInstance((s) => s.shifts);
  const instance = useMemo(
    () => ({ nurses, shifts, staff_weight: 1 } as Instance),
    [nurses, shifts]
  );

  const solutionId = useSolution((s) => s.solutionId);
  const solution = useSolution((s) => s.solution);
  const setSolution = useSolution((s) => s.setSolution);

  console.log("Solid"+solutionId);

  const [infeasibilityDetails, setInfeasibilityDetails] = useState<InfeasibilityDetails>({});

  const tableDataFromSolution = useMemo(
    () => instanceSolutionToTableData({ instance, solution }),
    [instance, solutionId]
  );

  const [data, setData] = useState<any[]>([]);
  const isRehydratingRef = React.useRef(false);

  useEffect(() => {
    // when a new solution is selected externally, rehydrate the UI from it
    if (instance.nurses.length === 0 || instance.shifts.length === 0) return;

    isRehydratingRef.current = true;
    setData(tableDataFromSolution);
  }, [tableDataFromSolution, instance.nurses, instance.shifts]);

  useEffect(() => {

    if (isRehydratingRef.current) {
      isRehydratingRef.current = false;
      return;
    }

    updateSolutionToView();
  }, [data]);

  const [feasible, setFeasible] = useState(true);
  const [solutionValue, setSolutionValue] = useState(0);
  useEffect(() => {
    calculateObjective();
  }, [solution]);

  useEffect(() => {
    checkFeasibility();
  }, [solution]);

  return (
    <div className="flex flex-col p-4 gap-4 h-full w-full">
      
        <Tooltip title="test" disableInteractive>
          <h1 className="text-2xl font-bold pb-2 mb-4 border-b border-border">
            Project [id]
          </h1>
        </Tooltip>
      
      <div className="p-4 flex flex-col gap-4 w-full h-[100vh] overflow-y-scroll">
        <div className="flex gap-4">
        <NurseTable tableData={data} setTableData={setData} instance={instance} infeasibilityDetails={infeasibilityDetails}/>
        </div>
        <div className="flex justify-end">
          <p className="mr-4 self-center text-sm text-gray-600">
            {`Objective: ${solutionValue}`}
          </p>
          
            {feasible ? 
              <p className="mr-4 self-center text-sm text-green-600">
                feasible 
              </p> : 
              <p className="mr-4 self-center text-sm text-red-600">
                infeasible
              </p>
            }
          
        </div>
      </div>
    </div>
  );

  
  function checkFeasibility() {
    
      console.log("Recalculating feasibility...");
      let isFeasible = true;
      const newDetails: InfeasibilityDetails = {};




      // work time
      instance.nurses.forEach((nurse) => {
        let totalWorkTime = 0;
        instance.shifts.forEach((shift) => {
          const assignedNurses = solution[shift.uid] || [];
          if (assignedNurses.includes(nurse.uid)) {
            const shiftDuration = (new Date(shift.end_time).getTime() - new Date(shift.start_time).getTime()) / (1000 * 60);
            totalWorkTime += shiftDuration;
          }
        });
        if (totalWorkTime < nurse.minimum_work_time || totalWorkTime > nurse.maximum_work_time) {

          instance.shifts.forEach((shift) => {
            const shiftDate = getShiftDate(shift);
            const assignedNurses = solution[shift.uid] || [];
            if (!assignedNurses.includes(nurse.uid)) {
              if (totalWorkTime < nurse.minimum_work_time) {
                addReason(
                  nurse.uid,
                  shiftDate,
                  `Total work time (${totalWorkTime} mins) is less than minimum required (${nurse.minimum_work_time} mins)`,
                  newDetails
                );
              }
            } else if (totalWorkTime > nurse.maximum_work_time) {
              addReason(
                nurse.uid,
                shiftDate,
                `Total work time (${totalWorkTime} mins) is more than maximum allowed (${nurse.maximum_work_time} mins)`,
                newDetails
              );
            }
          });

          isFeasible = false;
        }
      });



      instance.nurses.forEach((nurse) => {
        const nurseConsecutives = getConsecutivesArrayForNurse({ instance, solution, nurseUid: nurse.uid });
        // minimum consecutive shifts
        nurseConsecutives.forEach((consecutive) => {
          if (consecutive.on &&
            consecutive.count < nurse.minimum_consecutive_shifts &&
            getFirstDateOfInstance(instance) !== consecutive.startDate &&
            getLastDateOfInstance(instance) !== new Date(new Date(consecutive.startDate).getTime() + ((consecutive.count - 1) * 24 * 60 * 60 * 1000)).toISOString().split("T")[0]) {
            const shiftDate = consecutive.startDate;
            for (let i = 0; i < consecutive.count; i++) {
              const currentDate = new Date(new Date(shiftDate).getTime() + (i * 24 * 60 * 60 * 1000)).toISOString().split("T")[0];
              addReason(
                nurse.uid,
                currentDate,
                `Assigned to ${consecutive.count} consecutive shifts, which is less than minimum required (${nurse.minimum_consecutive_shifts})`,
                newDetails
              );
            }
            isFeasible = false;
          }

          // maximum consecutive shifts
          if (consecutive.on &&
            consecutive.count > nurse.maximum_consecutive_shifts) {
            const shiftDate = consecutive.startDate;
            for (let i = 0; i < consecutive.count; i++) {
              const currentDate = new Date(new Date(shiftDate).getTime() + (i * 24 * 60 * 60 * 1000)).toISOString().split("T")[0];
              addReason(
                nurse.uid,
                currentDate,
                `Assigned to ${consecutive.count} consecutive shifts, which is more than maximum allowed (${nurse.maximum_consecutive_shifts})`,
                newDetails
              );
            }
            isFeasible = false;
          }

          // minimum days off
          if (!consecutive.on &&
            consecutive.count < nurse.minimum_consecutive_days_off &&
            getFirstDateOfInstance(instance) !== consecutive.startDate &&
            getLastDateOfInstance(instance) !== new Date(new Date(consecutive.startDate).getTime() + ((consecutive.count - 1) * 24 * 60 * 60 * 1000)).toISOString().split("T")[0]) {
            const shiftDate = consecutive.startDate;
            for (let i = 0; i < consecutive.count; i++) {
              const currentDate = new Date(new Date(shiftDate).getTime() + (i * 24 * 60 * 60 * 1000)).toISOString().split("T")[0];
              addReason(
                nurse.uid,
                currentDate,
                `Has ${consecutive.count} consecutive days off, which is less than minimum required (${nurse.minimum_consecutive_days_off})`,
                newDetails
              );
            }
            isFeasible = false;
          }
        });

      });

      // shift rotation
      instance.nurses.forEach((nurse) => {
        instance.shifts.forEach((shift) => {
          const assignedNurses = solution[shift.uid] || [];
          if (assignedNurses.includes(nurse.uid)) {
            shift.not_followed_by_shift_types.forEach((notAllowedType) => {

              const nextDate = new Date(new Date(shift.start_time).getTime() + (2 * 24 * 60 * 60 * 1000)).toISOString().split("T")[0];
              const nextShifts = instance.shifts.filter(s => s.start_time.split("T")[0] === nextDate && s.type === notAllowedType);
              nextShifts.forEach((nextShift) => {
                const nextAssignedNurses = solution[nextShift.uid] || [];
                if (nextAssignedNurses.includes(nurse.uid)) {
                  addReason(
                    nurse.uid,
                    nextDate,
                    `Assigned to shift type ${notAllowedType} preceded by ${shift.type} not allowed.`,
                    newDetails
                  );
                  isFeasible = false;
                }
              });
            });
          }
        });
      });

      // maximum number of shift types
      instance.nurses.forEach((nurse) => {
        const shiftTypeCounts: Record<string, number> = {};
        instance.shifts.forEach((shift) => {
          const assignedNurses = solution[shift.uid] || [];
          if (assignedNurses.includes(nurse.uid)) {
            shiftTypeCounts[shift.type] = (shiftTypeCounts[shift.type] || 0) + 1;
          }
        });
        Object.entries(shiftTypeCounts).forEach(([type, count]) => {
          const maxAllowed = nurse.maximum_number_of_shifts_per_type[type] || 0;
          if (count > maxAllowed) {
            console.log(`Nurse ${nurse.name} assigned to ${count} shifts of type ${type}, which is more than maximum allowed (${maxAllowed})`);
            instance.shifts.forEach((shift) => {
              const shiftDate = getShiftDate(shift);
              const assignedNurses = solution[shift.uid] || [];
              if (assignedNurses.includes(nurse.uid) && shift.type === type) {
                addReason(
                  nurse.uid,
                  shiftDate,
                  `Assigned to ${count} shifts of type ${type}, which is more than maximum allowed (${maxAllowed})`,
                  newDetails
                );
              }
            });
            isFeasible = false;
          }
        });
      });

      // maximum number of weekends
      instance.nurses.forEach((nurse) => {
        let weekendCount = 0;
        let checkedWeekendShiftUids = new Set<shiftUid>();
        const weekendOnDates: string[] = [];
        instance.shifts.forEach((shift) => {
          if (checkedWeekendShiftUids.has(shift.uid)) return;
          const assignedNurses = solution[shift.uid] || [];
          if (!assignedNurses.includes(nurse.uid)) return;
          const shiftDate = getShiftDate(shift);
          const dateObj = new Date(shiftDate);
          const isSunday = dateObj.getDay() === 0;
          const isSaturday = dateObj.getDay() === 6;

          if (isSaturday) {
            const nextDate = new Date(dateObj.getTime() + (24 * 60 * 60 * 1000)).toISOString().split("T")[0];
            const nextShifts = instance.shifts.filter(s => s.start_time.split("T")[0] === nextDate);
            const weekendShifts = instance.shifts.filter(s => s.start_time.split("T")[0] === shiftDate || s.start_time.split("T")[0] === nextDate);
            weekendOnDates.push(shiftDate);
            if (nextShifts.some(s => {
              const assignedNurses = solution[s.uid] || [];
              return assignedNurses.includes(nurse.uid);
            })) {
              weekendOnDates.push(nextDate);
            }
            weekendShifts.forEach(s => checkedWeekendShiftUids.add(s.uid));
            weekendCount++;
          } else if (isSunday) {
            const prevDate = new Date(dateObj.getTime() - (24 * 60 * 60 * 1000)).toISOString().split("T")[0];
            const prevShifts = instance.shifts.filter(s => s.start_time.split("T")[0] === prevDate);
            const weekendShifts = instance.shifts.filter(s => s.start_time.split("T")[0] === shiftDate || s.start_time.split("T")[0] === prevDate);
            weekendOnDates.push(shiftDate);
            if (prevShifts.some(s => {
              const assignedNurses = solution[s.uid] || [];
              return assignedNurses.includes(nurse.uid);
            })) {
              weekendOnDates.push(prevDate);
            }
            weekendShifts.forEach(s => checkedWeekendShiftUids.add(s.uid));
            weekendCount++;
          }
        });

        if (weekendCount > nurse.maximum_weekends) {
          console.log(`Nurse ${nurse.name} assigned to ${weekendCount} weekends, which is more than maximum allowed (${nurse.maximum_weekends}), ${weekendOnDates.join(", ")}`);
          weekendOnDates.forEach((date) => {
            addReason(
              nurse.uid,
              date,
              `Assigned to ${weekendCount} weekends, which is more than maximum allowed (${nurse.maximum_weekends})`,
              newDetails
            );
          });
          isFeasible = false;
        }

      });

      // blocked days
      instance.nurses.forEach((nurse) => {
        nurse.days_off.forEach((dayOff) => {
          instance.shifts.forEach((shift) => {
            const shiftDate = getShiftDate(shift);
            if (shiftDate === dayOff) {
              const assignedNurses = solution[shift.uid] || [];
              if (assignedNurses.includes(nurse.uid)) {
                addReason(
                  nurse.uid,
                  shiftDate,
                  `Assigned to shift on blocked day (${dayOff})`,
                  newDetails
                );
                isFeasible = false;
              }
            }
          });
        });
      });

      console.log(newDetails);
      setInfeasibilityDetails(newDetails);
      setFeasible(isFeasible);
  }

  function addReason (shiftUid: number, date: string, msg: string, newDetails: InfeasibilityDetails) {
    if (!newDetails[shiftUid]) {
      newDetails[shiftUid] = {};
    }

    if (!newDetails[shiftUid][date]) {
      newDetails[shiftUid][date] = new Set<string>();
    }

    newDetails[shiftUid][date].add(msg);
  }
  
  function calculateObjective() {
    
      let totalValue = 0;

      instance.nurses.forEach((nurse) => {
        const nurseId = nurse.uid;
        Object.keys(solution).forEach((shiftId) => {
          const assignedNurses = solution[shiftId];
          if (assignedNurses.includes(nurseId)) {
            const shift = instance.shifts.find(s => s.uid === Number(shiftId));
            if (shift) {
              totalValue += nurse.preferred_off_shift_weight[shift.uid.toString()] || 0;

              totalValue += nurse.staff ? 0 : instance.staff_weight;
            }
          } else {
            const shift = instance.shifts.find(s => s.uid === Number(shiftId));
            if (shift) {
              totalValue += nurse.preferred_shift_weight[shift.uid.toString()] || 0;
            }
          }
        });
      });

      instance.shifts.forEach((shift) => {
        const assignedNurses = solution[shift.uid] || [];
        const demand = shift.demand;
        const assignedCount = assignedNurses.length;

        if (assignedCount < demand) {
          totalValue += shift.weight_below_demand * (demand - assignedCount);
        } else if (assignedCount > demand) {
          totalValue += shift.weight_above_demand * (assignedCount - demand);
        }
      });

      setSolutionValue(totalValue);
  }
  
  function updateSolutionToView() {
    
    const newSolution: Solution = {};
    for (const nurseSchedule of data) {
      const nuid = Number(nurseSchedule["Nurse"]);
      for (const [date, shiftType] of Object.entries(nurseSchedule)) {
        if (date === "Nurse") continue;
        if (!shiftType) continue;
  
        const shift = instance.shifts.find(
          (s) => s.type === shiftType && s.start_time.split("T")[0] === date
        );
        if (!shift) continue;
  
        (newSolution[shift.uid] ??= []).push(nuid);
      }
    }
  
    setSolution(newSolution);
    
  }
}
