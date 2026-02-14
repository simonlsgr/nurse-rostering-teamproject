

export async function solve(json: unknown) {

  const res = await fetch("/api/solver", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(json),
  });

  const data = await res.json();

  if (!res.ok) throw new Error(data.error);

  return data;
}


export async function pollJob(jobId: string) {

  const res = await fetch(`/api/solver?taskId=${jobId}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  const data = await res.json();

  if (!res.ok) throw new Error(data.error);

  return data;
}