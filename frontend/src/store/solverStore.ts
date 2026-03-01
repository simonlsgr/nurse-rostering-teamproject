import { Job } from "@/types/solverVars";
import { create } from "zustand";

type JobsState = {

  jobs: Record<string, Job>;
  setJobs: (jobs: Record<string, Job> | ((prev: Record<string, Job>) => Record<string, Job>)) => void;
  updateJob: (job: Job) => void;
  removeJob: (job: Job) => void;
};

export const useJobs = create<JobsState>((set) => ({

  jobs: {},
  setJobs: (jobs) => set((state) => ({ jobs: typeof(jobs) === "function" ? jobs(state.jobs) : jobs})),
  updateJob: (job: Job) =>
    set((state) => ({
      jobs: {
        ...state.jobs,
        [job.task_id]: job,
      },
    })),
  removeJob: (job: Job) =>
    set((state) => {
      const { [job.task_id]: _, ...remaining } = state.jobs;
      return { jobs: remaining };
    }),
}));
