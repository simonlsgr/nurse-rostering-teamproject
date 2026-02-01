

export default async function ProjectPage({ params }: { params: { projectId: string } }){  
  
  const nurses = [
    {id: 1, name: "Max Mustermann"},
    {id: 2, name: "Max Mustermann2"}
  ]


  return (

    <div className="flex h-screen gap-2">
      
      {/* sidebar left*/}
      <div className="w-[10vw] min-w-[240px] max-w-[320px] border-r bg-gray-200">
      </div>
      
      
      <div className="w-full">
      
        {/* topbar */}
        <div className="h-[2vw] min-h-[30px] max-h-[40px] hidden">
        </div>
      
        {/* main view */}
        <div className="p-2">
      
          <h1 className="text-2xl font-bold pb-2 mb-4 border-b">
            Project [id]
          </h1>
      
       
        </div>
      
      </div>

      {/* sidebar right */}
      <div className="w-[10vw] min-w-[240px] max-w-[320px] border-l">


        <div className="border-b h-[50vh] content-between overflow-auto">
          <p className="p-2"> All Nurses: </p>

          {nurses.map((nurse) => (

            <div 
              className="border rounded-lg w-[calc(100%-1rem)] h-20 p-2 mb-2 ml-2 mt-2" 
              key={nurse.id}
            >
              <p className=""> Name: {nurse.name} </p>              
              <p> ID: {nurse.id} </p> 


            </div>

          ))}

        </div>


      </div>
    
    </div>
  );
}