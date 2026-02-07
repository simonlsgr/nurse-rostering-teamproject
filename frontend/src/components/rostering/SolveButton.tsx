"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useJsonData } from "@/store/JsonStore";


export default function SolveButton() {


  const { jsonData } = useJsonData();
  
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSolve = async () => {

    try {

      setLoading(true);
      setError(null);

      const res = await fetch("/api/solver", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(jsonData),
      });
      
      if (!res.ok) throw new Error("Solver request failed");
      const data = await res.json();
      setResult(data);

    } catch (err: any) {
      setError(err.message);
      setResult(null);

    } finally {
      setLoading(false);
    }
  }


  return (

    <div>
      <div className="p-4">
      <Button
        className="mt-2 px-4 py-2 bg-gray-800 text-white rounded"
        onClick={handleSolve}
        disabled={loading}
      >
        {loading ? "Solving..." : "Solve"}
      </Button>
      {error && <p className="text-red-600 mt-2">{error}</p>}
      {result && (
        <pre className="mt-4 bg-gray-100 p-2 rounded overflow-auto">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
    </div>

  );
}


{/* <Button onClick={handleSolve}> Solve </Button> */}
