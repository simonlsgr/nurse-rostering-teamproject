import { NextResponse } from "next/server";

const solverUrl = process.env.SOLVER_API_URL;



export async function GET(req: Request) {

  const { searchParams } = new URL(req.url);
  const projectId = searchParams.get("projectId");
  const solutionId = searchParams.get("solutionId");

  if (!solverUrl) {
    return NextResponse.json(
      { error: "SOLVER_API_URL not set" },
      { status: 500 }
    );
  }

  if (!projectId) {
    return NextResponse.json(
      { error: "Project ID not provided" },
      { status: 500 }
    );
  }

  const res = await fetch(`${solverUrl}/projects/${projectId}/solutions${solutionId ? `/${solutionId}` : ""}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  const data = await res.json();

  if (!res.ok) {
    return NextResponse.json(
      { error: data.detail ?? "Failed to get solution from backend" },
      { status: 500 }
    );
  }


  return NextResponse.json(data);
}



export async function POST(req: Request) {
  const body = await req.json();
  
  const { searchParams } = new URL(req.url);
  const projectId = searchParams.get("projectId");


  if (!solverUrl) {
    return NextResponse.json(
      { error: "SOLVER_API_URL not set" },
      { status: 500 }
    );
  }

  if (!projectId) {
    return NextResponse.json(
      { error: "Project ID not provided" },
      { status: 500 }
    );
  }

  const res = await fetch(`${solverUrl}/projects/${projectId}/solutions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  const data = await res.json();

  if (!res.ok) {
    return NextResponse.json(
      { error: data.detail ?? "Failed to post solution to backend" },
      { status: 500 }
    );
  }



  return NextResponse.json(data);
}


export async function PUT(req: Request) {
  const body = await req.json();
  
  const { searchParams } = new URL(req.url);
  const projectId = searchParams.get("projectId");
  const solutionId = searchParams.get("solutionId");

  if (!solverUrl) {
    return NextResponse.json(
      { error: "SOLVER_API_URL not set" },
      { status: 500 }
    );
  }

  if (!projectId) {
    return NextResponse.json(
      { error: "Project ID not provided" },
      { status: 500 }
    );
  }

  const res = await fetch(`${solverUrl}/projects/${projectId}/solutions/${solutionId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  const data = await res.json();

  if (!res.ok) {
    return NextResponse.json(
      { error: data.detail ?? "Failed to edit solution in backend" },
      { status: 500 }
    );
  }



  return NextResponse.json(data);
}


export async function DELETE(req: Request) {

  const { searchParams } = new URL(req.url);
  const projectId = searchParams.get("projectId");
  const solutionId = searchParams.get("solutionId");

  if (!solverUrl) {
    return NextResponse.json(
      { error: "SOLVER_API_URL not set" },
      { status: 500 }
    );
  }

  if (!projectId) {
    return NextResponse.json(
      { error: "Project ID not provided" },
      { status: 500 }
    );
  }

  const res = await fetch(`${solverUrl}/projects/${projectId}/solutions/${solutionId}`, {
    method: "DELETE",
  });

  const data = await res.json();

  if (!res.ok) {
    return NextResponse.json(
      { error: data.detail ?? "Failed to delete solution in backend" },
      { status: 500 }
    );
  }



  return NextResponse.json(data);
}