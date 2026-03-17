import { Nurse, Shift } from "@/types/nurseVars";
import { create } from "zustand";
import { useNurses } from "./nurseStore";



// instance within a project, containing all the data of the problem
type InstanceState = {

  // proxy for nurse state
	nurses: Nurse[];
	setNurses: (nurses: Nurse[]) => void;

	shifts: Shift[];
	staff_weight: number;
	setShifts: (shifts: Shift[]) => void;
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

	shifts: [],
	staff_weight: 1,
	setShifts: (shifts) => set({ shifts }),
	setStaffWeight: (staff_weight) => set({ staff_weight }),
	setInstance: (instance) => {
    useNurses.getState().setNurses(instance.nurses);

    set({
      shifts: instance.shifts, 
      staff_weight: instance.staff_weight,
    });
  }
}));

