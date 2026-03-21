import { NextResponse } from "next/server";

const solverUrl = process.env.SOLVER_API_URL;



export async function GET(req: Request) {

  const { searchParams } = new URL(req.url);
  const projectId = searchParams.get("projectId");
  const shiftId = searchParams.get("shiftId");

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

  const res = await fetch(`${solverUrl}/projects/${projectId}/shifts`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  const data = await res.json();

  if (!res.ok) {
    return NextResponse.json(
      { error: data.detail ?? "Failed to get shifts from backend" },
      { status: 500 }
    );
  }


  return NextResponse.json(data);
}



export async function POST(req: Request) {
  const body = await req.json();
  
  const { searchParams } = new URL(req.url);
  const projectId = searchParams.get("projectId");
  const bulk = searchParams.get("bulk");
  const del = searchParams.get("del");


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

  const res = await fetch(`${solverUrl}/projects/${projectId}/shifts${bulk ? (del ? `/bulk-delete` : `/bulk-create`) : ""}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  const data = await res.json();

  if (!res.ok) {
    return NextResponse.json(
      { error: data.detail ?? "Failed to post shift to backend" },
      { status: 500 }
    );
  }



  return NextResponse.json(data);
}


export async function PUT(req: Request) {
  const body = await req.json();
  
  const { searchParams } = new URL(req.url);
  const projectId = searchParams.get("projectId");
  const shiftId = searchParams.get("shiftId");

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
  
  if (!shiftId) {
    return NextResponse.json(
      { error: "Shift ID not provided" },
      { status: 500 }
    );
  }

  const res = await fetch(`${solverUrl}/projects/${projectId}/shifts/${shiftId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  const data = await res.json();

  if (!res.ok) {
    return NextResponse.json(
      { error: data.detail ?? "Failed to edit shift in backend" },
      { status: 500 }
    );
  }



  return NextResponse.json(data);
}


export async function DELETE(req: Request) {

  const { searchParams } = new URL(req.url);
  const projectId = searchParams.get("projectId");
  const shiftId = searchParams.get("shiftId");

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

  if (!shiftId) {
    return NextResponse.json(
      { error: "Shift ID not provided" },
      { status: 500 }
    );
  }

  const res = await fetch(`${solverUrl}/projects/${projectId}/shifts/${shiftId}`, {
    method: "DELETE",
  });

  const data = await res.json();

  if (!res.ok) {
    return NextResponse.json(
      { error: data.detail ?? "Failed to delete shift in backend" },
      { status: 500 }
    );
  }



  return NextResponse.json(data);
}