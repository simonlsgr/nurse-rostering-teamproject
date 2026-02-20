import { Nurse } from "@/types/nurseVars";
import { create } from "zustand";




// those nurses selected in the NurseList
type NurseListSelectionState = {

  selectedNurses: Nurse[];
  setSelectedNurses: (selectedNurses: Nurse[] | ((prev: Nurse[]) => Nurse[])) => void;
};

export const useNurseListSelection = create<NurseListSelectionState>((set) => ({

  selectedNurses: [],
  setSelectedNurses: (selectedNurses) => set((state) => ({ selectedNurses: typeof(selectedNurses) === "function" ? selectedNurses(state.selectedNurses) : selectedNurses}))
}));
