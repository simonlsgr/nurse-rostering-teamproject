import { SolutionEntry } from "@/store/solutionStore";

export async function createSolution(solutionEntry: SolutionEntry, projectId: string) {

  const res = await fetch(`/api/solution_entry?projectId=${projectId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(solutionEntry),
  });

  const data = await res.json();

  if (!res.ok) throw new Error(JSON.stringify(data.error));

  return data as SolutionEntry;

}

export async function getAllSolutions(projectId: string) {

  const res = await fetch(`/api/solution_entry?projectId=${projectId}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  const data = await res.json();

  if (!res.ok) throw new Error(data.error);

  return data as SolutionEntry[];
}

export async function getSolution(solutionId: string, projectId: string) {

  const res = await fetch(`/api/solution_entry?projectId=${projectId}&solutionId=${solutionId}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  const data = await res.json();

  if (!res.ok) throw new Error(data.error);

  return data as SolutionEntry;
}

export async function editSolution(editedSolution: SolutionEntry, projectId: string) {

  const res = await fetch(`/api/solution_entry?projectId=${projectId}&solutionId=${editedSolution.solutionId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(editedSolution),
  });

  const data = await res.json();

  if (!res.ok) throw new Error(data.error);

  return data as SolutionEntry;
}

export async function deleteSolution(solutionId: string, projectId: string) {
  
  const res = await fetch(`/api/solution_entry?projectId=${projectId}&solutionId=${solutionId}`, {
    method: "DELETE",
  });

  const data = await res.json();

  if (!res.ok) throw new Error(data.error);
}