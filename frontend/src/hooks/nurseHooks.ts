import { useNurses } from "@/store/nurseStore";



export function useLoadNurses(){

  const { setNurses } = useNurses();

  const loadNurses = async() => {
    const data = [
      {id: "1", name: "Max Mustermann"},
      {id: "2", name: "Max Mustermann2"}
    ];              // await fetchNurses(); <- TODO: implement api-call, doesnt have to be another helper-function
    
    setNurses(data);
  };

  return { loadNurses };
}