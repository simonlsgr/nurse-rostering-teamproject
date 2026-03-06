import { Nurse } from "@/types/nurseVars";
import { create } from "zustand";




type NursesState = {

  nurses: Nurse[];
  setNurses: (nurses: Nurse[] | ((prev: Nurse[]) => Nurse[])) => void;
  updateNurse: (nurse: Nurse) => void;
  removeNurse: (nurseId: number) => void;
};


export const useNurses = create<NursesState>((set) => ({

  nurses: [],
  setNurses: (nurses) => set((state) => ({ nurses: typeof(nurses) === "function" ? nurses(state.nurses) : nurses})),
  updateNurse: (updatedNurse: Nurse) =>
    set((state) => ({
      nurses: state.nurses.map((n) =>
        n.uid === updatedNurse.uid ? updatedNurse : n
      ),
    })),
  removeNurse: (nurseId: number) =>
    set((state) => ({
      nurses: state.nurses.filter((n) => n.uid !== nurseId),
    })),
}));


type DetailViewNurseState = {
  detailViewNurse: Nurse | null;
  setDetailViewNurse: (detailViewNurse: Nurse | null) => void;
};



export const useDetailViewNurse = create<DetailViewNurseState>((set) => ({

  detailViewNurse: null,
  setDetailViewNurse: (detailViewNurse) => set({ detailViewNurse }),

}));

type OpenNurseDetailViewState = {

  openNurseDetailView: boolean;
  setOpenNurseDetailView: (openNurseDetailView: boolean) => void;
};

export const useOpenNurseDetailView = create<OpenNurseDetailViewState>((set) => ({

  openNurseDetailView: false,
  setOpenNurseDetailView: (openNurseDetailView) => set({ openNurseDetailView }),

}));