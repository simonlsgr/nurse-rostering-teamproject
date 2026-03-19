import { NextResponse } from "next/server"
import { jobsQueue } from "../store"

export async function GET() {
const jobs = [...jobsQueue];

  jobsQueue.length = 0;

  return NextResponse.json(jobs);
}