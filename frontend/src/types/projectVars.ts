


export type Project = {

  id: string;
  name: string;
  shift_types?: ShiftType[];
  planning_horizon?: [start_date: string, end_date: string];
  created_at?: string
  last_modified?: string;

};


export type ShiftType = {
  id: string;
  name: string;
  duration: string; // // HH:mm:ss
  start: string; // "HH:mm"
  end: string;
  not_followed_by_shift_types: string[]
};