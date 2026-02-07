import { NextResponse } from "next/server";

const solverUrl = process.env.SOLVER_API_URL;

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

  if (!res.ok) {
    return NextResponse.json(
      { error: "Solver failed" },
      { status: 500 }
    );
  }

  const data = await res.json();

  return NextResponse.json(data);
}
