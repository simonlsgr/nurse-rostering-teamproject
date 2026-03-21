import { Shift } from "@/types/nurseVars";

export async function createShift(shift: Shift, projectId: string) {

  const res = await fetch(`/api/shifts?projectId=${projectId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(shift),
  });

  const data = await res.json();

  if (!res.ok) throw new Error(JSON.stringify(data.error));

  return data as Shift;

}

export async function createShifts(shifts: Shift[], projectId: string) {

  const res = await fetch(`/api/shifts?projectId=${projectId}&bulk=${true}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({shifts}),
  });

  const data = await res.json();

  if (!res.ok) throw new Error(JSON.stringify(data.error));

  return data as Shift[];

}


export async function getAllShifts(projectId: string) {

  const res = await fetch(`/api/shifts?projectId=${projectId}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  const data = await res.json();

  if (!res.ok) throw new Error(data.error);

  return data as Shift[];
}

export async function editShift(editedShift: Shift, projectId: string) {

  const res = await fetch(`/api/shifts?projectId=${projectId}&shiftId=${editedShift.id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(editedShift),
  });

  const data = await res.json();

  if (!res.ok) throw new Error(data.error);

  return data as Shift;
}

export async function deleteShift(shiftId: string, projectId: string) {
  
  const res = await fetch(`/api/shifts?projectId=${projectId}&shiftId=${shiftId}`, {
    method: "DELETE",
  });

  const data = await res.json();

  if (!res.ok) throw new Error(data.error);
}


export async function deleteShifts(shiftIds: string[], projectId: string) {
  
  const payload = { "shift_ids": shiftIds };

  const res = await fetch(`/api/shifts?projectId=${projectId}&bulk=${true}&del=${true}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),  
  });

  const data = await res.json();

  if (!res.ok) throw new Error(data.error);
}