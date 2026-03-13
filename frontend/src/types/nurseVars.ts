

export type Nurse = {
  db_id?: string; // from database
  uid: number;
  name: string;
  preferred_shifts: number[];
  preferred_off_shifts: number[];
  blocked_shifts: number[];
  days_off: string[];
  staff: boolean;
  min_time_between_shifts: string;
  preferred_shift_weight: Record<string, number>; // fix later so that it is only nubmer
  preferred_off_shift_weight: Record<string, number>;
  minimum_work_time: number;
  maximum_work_time: number;
  minimum_consecutive_shifts: number;
  maximum_consecutive_shifts: number;
  minimum_consecutive_days_off: number;
  maximum_weekends: number;
  maximum_number_of_shifts_per_type: Record<string, number>;
}

export type Shift = {
  db_id?: string; // for later
  uid: number;
  name: string;
  start_time: string;
  end_time: string;
  demand: number;
  type: string;
  not_followed_by_shift_types: string[];
  weight_below_demand: number;
  weight_above_demand: number;
}

export type Instance = {
  nurses: Nurse[];
  shifts: Shift[];
  staff_weight: number;
}

export type Solution = Record<string, any>;