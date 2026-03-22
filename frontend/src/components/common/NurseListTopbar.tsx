import AddIcon from '@mui/icons-material/Add';
import CreateNurseDialog from './CreateNurseDialog';
import NurseListMenuButton from './NurseListMenuButton';


export default function NurseListTopbar() {



  return (
    <div className="flex justify-between items-center pr-1">
    <p className="p-2"> All Nurses: </p>

    <div className="flex gap-1">
      <CreateNurseDialog />
      <NurseListMenuButton />
    </div>
  
  </div>
  )
}