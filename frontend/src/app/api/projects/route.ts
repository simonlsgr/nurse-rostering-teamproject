import { NextResponse } from "next/server";

const solverUrl = process.env.SOLVER_API_URL;



export async function GET(req: Request) {

  const { searchParams } = new URL(req.url);
  const projectId = searchParams.get("projectId");
  
  if (!solverUrl) {
    return NextResponse.json(
      { error: "SOLVER_API_URL not set" },
      { status: 500 }
    );
  }

  const res = await fetch(`${solverUrl}/projects${projectId ? `/${projectId}` : ""}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  const data = await res.json();

  if (!res.ok) {
    return NextResponse.json(
      { error: data.detail ?? "Failed to get project from backend" },
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

  const res = await fetch(`${solverUrl}/projects`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  const data = await res.json();

  if (!res.ok) {
    return NextResponse.json(
      { error: data.detail ?? "Failed to post project to backend" },
      { status: 500 }
    );
  }



  return NextResponse.json(data);
}


export async function PUT(req: Request) {
  const body = await req.json();
  
  const { searchParams } = new URL(req.url);
  const projectId = searchParams.get("projectId");

  if (!solverUrl) {
    return NextResponse.json(
      { error: "SOLVER_API_URL not set" },
      { status: 500 }
    );
  }

  const res = await fetch(`${solverUrl}/projects/${projectId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  const data = await res.json();

  if (!res.ok) {
    return NextResponse.json(
      { error: data.detail ?? "Failed to edit project in backend" },
      { status: 500 }
    );
  }



  return NextResponse.json(data);
}


export async function DELETE(req: Request) {

  const { searchParams } = new URL(req.url);
  const projectId = searchParams.get("projectId");

  if (!solverUrl) {
    return NextResponse.json(
      { error: "SOLVER_API_URL not set" },
      { status: 500 }
    );
  }

  const res = await fetch(`${solverUrl}/projects/${projectId}`, {
    method: "DELETE",
  });

  const data = await res.json();

  if (!res.ok) {
    return NextResponse.json(
      { error: data.detail ?? "Failed to delete project in backend" },
      { status: 500 }
    );
  }



  return NextResponse.json(data);
}