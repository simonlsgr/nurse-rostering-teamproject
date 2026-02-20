import { Nurse, Shift } from "@/types/nurseVars";
import { create } from "zustand";



// instance within a project, containing all the data of the problem
type InstanceState = {

	nurses: Nurse[];
	shifts: Shift[];
	staff_weight: number;
	setNurses: (nurses: Nurse[]) => void;
	setShifts: (shifts: Shift[]) => void;
	setStaffWeight: (staff_weight: number) => void;
	setInstance: (instance: { nurses: Nurse[], shifts: Shift[], staff_weight: number }) => void;
};

export const useInstance = create<InstanceState>((set) => ({

	nurses: [],
	shifts: [],
	staff_weight: 1,
	setShifts: (shifts) => set({ shifts }),
	setNurses: (nurses) => set({ nurses }),
	setStaffWeight: (staff_weight) => set({ staff_weight }),
	setInstance: (instance) => set({ nurses: instance.nurses, shifts: instance.shifts, staff_weight: instance.staff_weight }),
}));

