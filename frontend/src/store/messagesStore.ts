
import { create } from "zustand";




type MessagesState = {
    jobIds: string[]
    setJobIds: (jobIds: string[]) => void;
    addJobId: (jobId: string) => void;
    removeJobId: (id: string) => void;
};

export const useMessages = create<MessagesState>((set) => ({
  jobIds: [],
  setJobIds: (jobIds) => set({ jobIds }),
  addJobId: (jobId) => set((state) => ({ jobIds: [...state.jobIds, jobId] })),
  removeJobId: (id) =>
    set((state) => ({
      jobIds: state.jobIds.filter((j) => j !== id),
  })),
}));

