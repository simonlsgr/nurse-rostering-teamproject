import { NextResponse } from "next/server";

const solverUrl = process.env.SOLVER_API_URL;



export async function GET(req: Request) {

  const { searchParams } = new URL(req.url);
  const taskId = searchParams.get("taskId");
  
  if (!solverUrl) {
    return NextResponse.json(
      { error: "SOLVER_API_URL not set" },
      { status: 500 }
    );
  }

  if (!taskId) {
    return Response.json({ error: "Missing jobId" }, { status: 400 });
  }

  const res = await fetch(`${solverUrl}/jobs/${taskId}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  const data = await res.json();

  if (!res.ok) {
    return NextResponse.json(
      { error: data.detail ?? "Failed to get job from backend" },
      { status: 500 }
    );
  }


  return NextResponse.json(data);
}



export async function POST(req: Request) {
  const body = await req.json();
  
  if (!solverUrl) {
    return NextResponse.json(
      { error: "SOLVER_API_URL not set" },
      { status: 500 }
    );
  }

  const res = await fetch(`${solverUrl}/jobs`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  const data = await res.json();

  if (!res.ok) {
    return NextResponse.json(
      { error: data.detail ?? "Failed to post job to backend" },
      { status: 500 }
    );
  }



  return NextResponse.json(data);
}
