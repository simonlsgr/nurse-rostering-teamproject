import { useNurses } from "@/store/nurseStore";



export function useLoadNurses(){

  const { setNurses } = useNurses();

  const loadNurses = async() => {
    const data = [
      {id: "1", name: "Max Mustermann"},
      {id: "2", name: "aewfaweawef"},
      {id: "3", name: "gsge<ge<se"},
      {id: "4", name: "32523raf"},
      {id: "5", name: "gf<z34w"},
      {id: "6", name: "lfz87l"},
      {id: "7", name: "gw90sjhg9p"},
      {id: "8", name: "fk0ß39w4tuw09ht0phefsioedhfsw398h3ioöhshföoeihs"},
      {id: "9", name: "Otto"},

    ];              // await fetchNurses(); <- TODO: implement api-call, doesnt have to be another helper-function
    
    setNurses(data);
  };

  return { loadNurses };
}