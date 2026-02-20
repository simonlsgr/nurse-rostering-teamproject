'use client';
import { shiftUid, Consecutives } from "@/types/feasibilityHelperVars";
import { Instance, Shift, Solution } from "@/types/nurseVars";

export function instanceSolutionToTableData({ instance, solution }: { instance: Instance; solution: Solution; }) {

  const dates = instance.shifts.map((shift) => shift.start_time.split("T")[0]
  );

  const nurses = instance.nurses.map((nurse) => nurse.name);

  const nurseAtDates = instance.nurses.map(
    (nurse) => {
      const nurseSchedule: Record<string, string> = { "Nurse": nurse.uid.toString() };

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

export function getNurseByUid(instance: Instance, uid: number) {
  return instance.nurses.find((nurse) => nurse.uid === uid);
}


function getShiftByUid({ instance, shiftuid }: { instance: Instance; shiftuid: number; }) {
  return instance.shifts.find((shift) => { shift.uid === shiftuid; });
}


export function getShiftDate(shift: Shift) {
  return shift.start_time.split("T")[0];
}


export function getFirstDateOfInstance(instance: Instance) {
  if (instance.shifts.length === 0) return null;
  const dates = instance.shifts.map((shift) => shift.start_time.split("T")[0]);
  return dates.reduce((minDate, currentDate) => currentDate < minDate ? currentDate : minDate);
}


export function getLastDateOfInstance(instance: Instance) {
  if (instance.shifts.length === 0) return null;
  const dates = instance.shifts.map((shift) => shift.start_time.split("T")[0]);
  return dates.reduce((maxDate, currentDate) => currentDate > maxDate ? currentDate : maxDate);
}


// Helper for calculating consecutive shifts and days off for a nurse, used in feasibility checks
export function getConsecutivesArrayForNurse({ instance, solution, nurseUid }: { instance: Instance; solution: Solution; nurseUid: number; }) {
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


export function getDatesFromTableData(tableData: any[]) {
  if (tableData.length === 0) return [];
  return Object.keys(tableData[0]).filter(key => key !== "Nurse");
}


export function getShiftTypes(instance: Instance) {
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

