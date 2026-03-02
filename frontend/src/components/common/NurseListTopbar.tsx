import MoreVertIcon from '@mui/icons-material/MoreVert';
import AddIcon from '@mui/icons-material/Add';


export default function NurseListTopbar() {



  return (
    <div className="flex justify-between items-center pr-1">
    <p className="p-2"> All Nurses: </p>

    <div className="flex gap-1">
      <AddIcon 
        fontSize="small"
        className="hover:bg-gray-200 rounded text-muted-foreground"
      />
      <MoreVertIcon 
        fontSize="small"
        className="hover:bg-gray-200 rounded"          
      /> 
    </div>
  
  </div>
  )
}