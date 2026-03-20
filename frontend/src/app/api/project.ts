import { Project } from "@/types/projectVars";


export async function createProject(newProject: Project) {

  const res = await fetch("/api/projects", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(newProject),
  });

  const data = await res.json();

  if (!res.ok) throw new Error(data.error);

  return data as Project;
}

export async function getAllProjects() {

  const res = await fetch(`/api/projects`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  const data = await res.json();

  if (!res.ok) throw new Error(data.error);

  return data as Project[];
}


export async function getProject(projectId: string) {

  const res = await fetch(`/api/projects?projectId=${projectId}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  const data = await res.json();

  if (!res.ok) throw new Error(data.error);

  return data as Project;
}

export async function editProject(editedProject: Project) {

  const res = await fetch(`/api/projects?projectId=${editedProject.id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(editedProject),
  });

  const data = await res.json();

  if (!res.ok) throw new Error(data.error);

  return data as Project;
}

export async function deleteProject(projectId: string) {
  
  const res = await fetch(`/api/projects?projectId=${projectId}`, {
    method: "DELETE",
  });

  const data = await res.json();

  if (!res.ok) throw new Error(data.error);
}