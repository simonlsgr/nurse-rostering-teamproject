

export async function solve(json: unknown) {

  const res = await fetch("/api/solver", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(json),
  });

  if (!res.ok) throw new Error("Solve faileeeed");

  return res.json();
}
