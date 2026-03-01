

export async function fetchSolution(jobId: unknown) {

    const res = await fetch(`/api/solution?taskId=${jobId}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });
    
      const data = await res.json();
    
      if (!res.ok) throw new Error(data.error);
    
      return data;
}
  