export async function fetchFinishedJobs() {

    
    
    const res = await fetch("/api/webhooks/job_status/jobs", {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
        },
    })
      
    const jobs = await res.json();
    if (!res.ok) throw new Error();
    
    const jsonJobs = jobs.map((job: string) => JSON.parse(job));

    return jsonJobs;
}