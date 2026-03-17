import { Nurse } from "@/types/nurseVars";

export async function createNurse(nurse: Nurse, projectId: string) {

  const res = await fetch(`/api/nurses?projectId=${projectId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(nurse),
  });

  const data = await res.json();

  if (!res.ok) throw new Error(JSON.stringify(data.error));

  return data as Nurse;

}

export async function getAllNurses(projectId: string) {

  const res = await fetch(`/api/nurses?projectId=${projectId}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  const data = await res.json();

  if (!res.ok) throw new Error(data.error);

  return data as Nurse[];
}

export async function getNurse(nurseId: string, projectId: string) {

  const res = await fetch(`/api/projects?projectId=${projectId}&nurseId=${nurseId}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  const data = await res.json();

  if (!res.ok) throw new Error(data.error);

  return data as Nurse;
}

export async function editNurse(editedNurse: Nurse, projectId: string) {

  const res = await fetch(`/api/projects?projectId=${projectId}&nurseId=${editedNurse.id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ editedNurse }),
  });

  const data = await res.json();

  if (!res.ok) throw new Error(data.error);

  return data as Nurse;
}

export async function deleteNurse(nurseId: string, projectId: string) {
  
  const res = await fetch(`/api/projects?projectId=${projectId}&nurseId=${nurseId}`, {
    method: "DELETE",
  });

  const data = await res.json();

  if (!res.ok) throw new Error(data.error);
}