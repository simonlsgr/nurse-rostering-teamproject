import { Nurse, Shift } from "@/types/nurseVars";
import { create } from "zustand";
import { useNurses, useShifts } from "./nurseStore";



// instance within a project, containing all the data of the problem
type InstanceState = {

  // proxy for nurse state
	nurses: Nurse[];
	setNurses: (nurses: Nurse[]) => void;

	shifts: Shift[];
	setShifts: (shifts: Shift[]) => void;

	staff_weight: number;
	setStaffWeight: (staff_weight: number) => void;
	setInstance: (instance: { nurses: Nurse[], shifts: Shift[], staff_weight: number }) => void;
};

export const useInstance = create<InstanceState>((set) => ({

  // get and set nurses via the nurse state
  get nurses() {
    return useNurses.getState().nurses;
  },

  setNurses: (nurses: Nurse[]) => {
    useNurses.getState().setNurses(nurses);
  },


  get shifts() {
    return useShifts.getState().shifts;
  },

  setShifts: (shifts: Shift[]) => {
    useShifts.getState().setShifts(shifts);
  },

	staff_weight: 1,
	setStaffWeight: (staff_weight) => set({ staff_weight }),
	setInstance: (instance) => {
    useNurses.getState().setNurses(instance.nurses);
    useShifts.getState().setShifts(instance.shifts);
    set({
      staff_weight: instance.staff_weight,
    });
  }
}));

