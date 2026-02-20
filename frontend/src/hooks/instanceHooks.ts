import { useInstance } from "@/store/instanceStore";
import instanceData from "@/components/layout/Instance2.json";


export function useLoadInstance(){

  const { setInstance } = useInstance();

  const loadInstance = async() => {
    const data = instanceData;  
    
    setInstance(data);
  };

  return { loadInstance };
}
