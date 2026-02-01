import { Nurse } from "@/types/nurseVars";
import { create } from "zustand";



// all nuses whithin a project
type NursesState = {

  nurses: Nurse[];
  setNurses: (nurses: Nurse[]) => void;
};

export const useNurses = create<NursesState>((set) => ({

  nurses: [],
  setNurses: (nurses) => set({nurses})
}))



// those nurses selected in the NurseList
type NurseListSelectionState = {

  selectedNurses: Nurse[];
  setSelectedNurses: (selectedNurses: Nurse[]) => void;
};

export const useNurseListSelection = create<NurseListSelectionState>((set) => ({

  selectedNurses: [],
  setSelectedNurses: (selectedNurses) => set({selectedNurses})
}));
