

export type Job = {
  name: string;
  task_id: string;
  status: string;
  submitted_at: string;
  started_at: string | null;
  completed_at: string | null;
  error: string | null;
};