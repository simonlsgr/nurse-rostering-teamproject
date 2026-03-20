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

  const res = await fetch(`${solverUrl}/projects/${projectId}/shift_types`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  const data = await res.json();

  if (!res.ok) {
    return NextResponse.json(
      { error: data.detail ?? "Failed to get shift type from backend" },
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

  const res = await fetch(`${solverUrl}/projects/${projectId}/shift_types`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  const data = await res.json();

  if (!res.ok) {
    return NextResponse.json(
      { error: data.detail ?? "Failed to post shift type to backend" },
      { status: 500 }
    );
  }



  return NextResponse.json(data);
}


export async function PUT(req: Request) {
  const body = await req.json();
  
  const { searchParams } = new URL(req.url);
  const projectId = searchParams.get("projectId");
  const shiftTypeId = searchParams.get("shiftTypeId");


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

  if (!shiftTypeId) {
    return NextResponse.json(
      { error: "Shift type ID not provided" },
      { status: 500 }
    );
  }

  const res = await fetch(`${solverUrl}/projects/${projectId}/shift_types/${shiftTypeId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  const data = await res.json();

  if (!res.ok) {
    return NextResponse.json(
      { error: data.detail ?? "Failed to edit shift type in backend" },
      { status: 500 }
    );
  }



  return NextResponse.json(data);
}


export async function DELETE(req: Request) {

  const { searchParams } = new URL(req.url);
  const projectId = searchParams.get("projectId");
  const shiftTypeId = searchParams.get("shiftTypeId");

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

  if (!shiftTypeId) {
    return NextResponse.json(
      { error: "Shift type ID not provided" },
      { status: 500 }
    );
  }

  const res = await fetch(`${solverUrl}/projects/${projectId}/shift_types/${shiftTypeId}`, {
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