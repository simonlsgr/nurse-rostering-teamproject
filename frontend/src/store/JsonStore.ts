import { create } from "zustand";


// json input of the instance 
type JsonState = {

  jsonData: any | null;
  setJsonData: (jsonData: any) => void;
};

export const useJsonData = create<JsonState>((set) => ({

  jsonData: null,
  setJsonData: (jsonData) => set({jsonData})
}))