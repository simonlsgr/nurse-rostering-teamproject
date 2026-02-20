'use client';
export interface Consecutives {
  count: number;
  on: boolean;
  startDate: string;
}
type InfeasibilityReasonByDate = Record<string, Set<string>>;
export type shiftUid = number;
export type InfeasibilityDetails = Record<shiftUid, InfeasibilityReasonByDate>;
