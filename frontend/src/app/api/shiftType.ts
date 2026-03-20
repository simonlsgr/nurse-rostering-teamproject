import { ShiftType } from "@/types/projectVars";

export async function createShiftType(shiftType: ShiftType, projectId: string) {

  const res = await fetch(`/api/shift_types?projectId=${projectId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(shiftType),
  });

  const data = await res.json();

  if (!res.ok) throw new Error(JSON.stringify(data.error));

  return data as ShiftType;

}

export async function getShiftTypes(projectId: string) {

  const res = await fetch(`/api/shift_types?projectId=${projectId}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  const data = await res.json();

  if (!res.ok) throw new Error(data.error);

  return data as ShiftType[];
}

export async function editShiftType(editedShiftType: ShiftType, projectId: string) {

  const res = await fetch(`/api/shift_types?projectId=${projectId}&shiftTypeId=${editedShiftType.id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(editedShiftType),
  });

  const data = await res.json();

  if (!res.ok) throw new Error(data.error);

  return data as ShiftType;
}

export async function deleteShiftType(shiftTypeId: string, projectId: string) {
  
  const res = await fetch(`/api/shift_types?projectId=${projectId}&shiftTypeId=${shiftTypeId}`, {
    method: "DELETE",
  });

  const data = await res.json();

  if (!res.ok) throw new Error(data.error);
}