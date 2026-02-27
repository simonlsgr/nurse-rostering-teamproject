import { Consecutives, InfeasibilityDetails, shiftUid } from "@/types/feasibilityHelperVars";
import { Instance, Nurse, Solution } from "@/types/nurseVars";
import React from "react";
import { getShiftDate, getConsecutivesArrayForNurse, getFirstDateOfInstance, getLastDateOfInstance } from "./dataWrangler";


type SetFeasible = (value: boolean) => void;

export function addReason(shiftUid: number, date: string, msg: string, newDetails: InfeasibilityDetails) {
  if (!newDetails[shiftUid]) {
    newDetails[shiftUid] = {};
  }

  if (!newDetails[shiftUid][date]) {
    newDetails[shiftUid][date] = new Set<string>();
  }

  newDetails[shiftUid][date].add(msg);
}
export function calculateObjective(instance: Instance, solution: Solution) {
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

  return totalValue;
}

export function checkMaxConstraintsFeasibility(
  instance: Instance, 
  solution: Solution, 
  setInfeasibilityDetails: React.Dispatch<React.SetStateAction<InfeasibilityDetails>>, 
  setFeasible: SetFeasible
) {
  
  const newDetails: InfeasibilityDetails = {};

  const feasibilityResults = [
    checkMaximumWorktime(instance, solution, newDetails),
    checkMaximumConsecutivesOnly(instance, solution, newDetails),
    checkShiftRotation(instance, solution, newDetails),
    checkMaximumShiftsPerType(instance, solution, newDetails),
    checkMaximumWeekends(instance, solution, newDetails),
    checkBlockedDays(instance, solution, newDetails)
  ];

  const isFeasible = feasibilityResults.every(Boolean);

  setInfeasibilityDetails(newDetails);
  setFeasible(isFeasible);
}

export function checkFeasibility(
  instance: Instance, 
  solution: Solution, 
  setInfeasibilityDetails: React.Dispatch<React.SetStateAction<InfeasibilityDetails>>, 
  setFeasible: React.Dispatch<React.SetStateAction<boolean>>
) {

  
  let newDetails: InfeasibilityDetails = {};

  const feasibilityResults = [
    checkLimitedWorktime(instance, solution, newDetails),
    checkConsecutives(instance, solution, newDetails),
    checkShiftRotation(instance, solution, newDetails),
    checkMaximumShiftsPerType(instance, solution, newDetails),
    checkMaximumWeekends(instance, solution, newDetails),
    checkBlockedDays(instance, solution, newDetails)
  ];

  const isFeasible = feasibilityResults.every(Boolean);

  setInfeasibilityDetails(newDetails);
  setFeasible(isFeasible);
}

function checkBlockedDays(instance: Instance, solution: Solution, newDetails: InfeasibilityDetails) {
  let isFeasible = true;
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
  return isFeasible;
}

function checkMaximumWeekends(instance: Instance, solution: Solution, newDetails: InfeasibilityDetails) {
  let isFeasible = true;
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
  return isFeasible;
}

function checkMaximumShiftsPerType(instance: Instance, solution: Solution, newDetails: InfeasibilityDetails) {
  let isFeasible = true;
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
  return isFeasible;
}

function checkShiftRotation(instance: Instance, solution: Solution, newDetails: InfeasibilityDetails) {
  let isFeasible = true;
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
  return isFeasible;
}

function checkConsecutivesWrapper(instance: Instance, solution: Solution, newDetails: InfeasibilityDetails, checkMaxOnly: boolean) {
  let allFeasibilityResults: boolean[] = [];
  instance.nurses.forEach((nurse) => {
    const nurseConsecutives = getConsecutivesArrayForNurse({ instance, solution, nurseUid: nurse.uid });
    
    nurseConsecutives.forEach((consecutive) => {
      
      if (!checkMaxOnly) {
        allFeasibilityResults.push(
          checkMinimumConsecutives(consecutive, nurse, instance, newDetails),
          checkMinimumDaysOff(consecutive, nurse, instance, newDetails)
        );
      }

      allFeasibilityResults.push(
        checkMaximumConsecutives(consecutive, nurse, newDetails),
      );

    });

  });
  return allFeasibilityResults.every(Boolean);
}

function checkConsecutives(instance: Instance, solution: Solution, newDetails: InfeasibilityDetails) {
  const checkMaxOnly = false;
  return checkConsecutivesWrapper(instance, solution, newDetails, checkMaxOnly);
}

function checkMaximumConsecutivesOnly(instance: Instance, solution: Solution, newDetails: InfeasibilityDetails) {
  const checkMaxOnly = true;
  return checkConsecutivesWrapper(instance, solution, newDetails, checkMaxOnly);
}


function checkMinimumDaysOff(consecutive: Consecutives, nurse: Nurse, instance: Instance, newDetails: InfeasibilityDetails) {
  let isFeasible = true;
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
  return isFeasible;
}

function checkMaximumConsecutives(consecutive: Consecutives, nurse: Nurse, newDetails: InfeasibilityDetails) {
  let isFeasible = true;
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
  return isFeasible;
}

function checkMinimumConsecutives(consecutive: Consecutives, nurse: Nurse, instance: Instance, newDetails: InfeasibilityDetails) {
  let isFeasible = true;
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
  return isFeasible;
}

function checkLimitedWorktimeWrapper(instance: Instance, solution: Solution, newDetails: InfeasibilityDetails, checkMaxOnly: boolean) {
  let isFeasible = true;
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
        if (!assignedNurses.includes(nurse.uid)  && !checkMaxOnly) {
          if (totalWorkTime < nurse.minimum_work_time) {
            addReason(
              nurse.uid,
              shiftDate,
              `Total work time (${totalWorkTime} mins) is less than minimum required (${nurse.minimum_work_time} mins)`,
              newDetails
            );
            isFeasible = false;
          }
        } else if (totalWorkTime > nurse.maximum_work_time) {
          addReason(
            nurse.uid,
            shiftDate,
            `Total work time (${totalWorkTime} mins) is more than maximum allowed (${nurse.maximum_work_time} mins)`,
            newDetails
          );
          isFeasible = false;
        }
      });

      
    }
  });
  return isFeasible;

}

function checkLimitedWorktime(instance: Instance, solution: Solution, newDetails: InfeasibilityDetails, ) {
  const checkMaxOnly = false;
  return checkLimitedWorktimeWrapper(instance, solution, newDetails, checkMaxOnly);
}

function checkMaximumWorktime(instance: Instance, solution: Solution, newDetails: InfeasibilityDetails) {
  const checkMaxOnly = true;
  return checkLimitedWorktimeWrapper(instance, solution, newDetails, checkMaxOnly);
}

