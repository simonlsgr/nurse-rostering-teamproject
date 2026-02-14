import { Nurse, Shift } from "@/types/nurseVars";


export type Job = {
  name: string;
  task_id: string;
  status: string;
  submitted_at: string;
  started_at: string | null;
  completed_at: string | null;
  error: string | null;
};

export type NurseRosteringInstance = {
  nurses: Nurse[];
  shifts: Shift[];
  staff_weight: number;
};

export type SolverPayload = {
  nurse_rostering_instance: NurseRosteringInstance;
  optimization_parameters: any;
  solver: string;
  webhook_url?: string;
};