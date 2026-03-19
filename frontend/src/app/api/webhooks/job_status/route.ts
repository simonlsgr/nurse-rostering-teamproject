import { NextRequest, NextResponse } from "next/server"

import { Job } from "@/types/solverVars"
import { jobsQueue } from "./store"


export async function POST(req: NextRequest) {
  const data = await req.json()
  const job: Job = data as Job

  console.log("Webhook received:", job)

  jobsQueue.push(job)

  return NextResponse.json({ ok: true })
}


