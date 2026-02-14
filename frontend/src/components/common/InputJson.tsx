"use client";

import { useState } from "react";
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button";
import { useJsonData } from "@/store/JsonStore";


export default function JsonEditor() {

  const [text, setText] = useState('{\n  "example": 123\n}');
  const [error, setError] = useState<string | null>(null);

  const { jsonData, setJsonData } = useJsonData();


  const handleSave = () => {
    try {
      const parsed = JSON.parse(text);
      setJsonData(parsed);
      setError(null);

      // TODO: send JSON to backend
      
    } catch (e: any) {
      setError(e.message);
      console.error("Invalid JSON:", e);
    }
  };

  return (

    <div className="p-2 w-full max-w-lg h-120 overflow-auto">

      <p className="pb-2"> Input Instance: </p>

      <Textarea
        className="w-full h-60 p-2 border-gray-300 rounded font-mono"
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      {error && <p className="text-red-600 mt-2">Error: {error}</p>}

      <Button
        className="mt-2 px-4 py-2 bg-gray-800 text-white rounded"
        onClick={handleSave}
      >
        Save JSON
      </Button>

      {jsonData && (
        <pre className="mt-4 bg-gray-100 p-2 rounded overflow-auto">
          {JSON.stringify(jsonData, null, 2)}
        </pre>
      )}

    </div>
  );
}
