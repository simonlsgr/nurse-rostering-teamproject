import { Nurse } from "@/types/nurseVars";
import { create } from "zustand";




type NursesState = {

  nurses: Nurse[];
  setNurses: (nurses: Nurse[]) => void;
};


export const useNurses = create<NursesState>((set) => ({

  nurses: [],
  setNurses: (nurses) => set(({ nurses }))
}));


