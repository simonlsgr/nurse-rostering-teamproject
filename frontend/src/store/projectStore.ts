import ProjectCard from "@/components/ui/ProjectCard";
import { createDefaultNewProject } from "@/lib/utils";
import { NewProject, Project, ShiftType } from "@/types/projectVars";
import { create } from "zustand";


type ProjectsState = {

  projects: Record<string, Project>;
  setProjects: (projects: Record<string, Project> | ((prev: Record<string, Project>) => Record<string, Project>)) => void;
  updateProject: (project: Project) => void;
  removeProject: (projectId: string) => void;
};

export const useProjects = create<ProjectsState>((set) => ({

  projects: {},
  setProjects: (projects) => set((state) => ({ projects: typeof(projects) === "function" ? projects(state.projects) : projects})),
  updateProject: (project: Project) =>
    set((state) => ({
      projects: {
        ...state.projects,
        [project.id]: project,
      },
    })),
    removeProject: (projectId: string) =>
      set((state) => {
        const { [projectId]: _, ...rest } = state.projects;
        return { projects: rest };
    }),
}));


type SelectedProjectState = {

  selectedProject: Project | null;
  setSelectedProject: (project: Project | null) => void;
};

export const useSelectedProject = create<SelectedProjectState>((set) => ({

  selectedProject: null,
  setSelectedProject: (selectedProject) => set({ selectedProject }),
}));

type NewProjectState = {

  newProject: NewProject;
  setNewProject: (newProject: NewProject | ((prev: NewProject) => NewProject)) => void; 
};

export const useNewProject = create<NewProjectState>((set) => ({

  newProject: createDefaultNewProject(),
  setNewProject: (newProject) => set((state) => ({ newProject: typeof(newProject) === "function" ? newProject(state.newProject) : newProject})),
}));



type ShiftTypesState = {

  shiftTypes: ShiftType[];
  setShiftTypes: (shiftTypes: ShiftType[] | ((prev: ShiftType[]) => ShiftType[])) => void;
};

export const useShiftTypes = create<ShiftTypesState>((set) => ({

  shiftTypes: [],
  setShiftTypes: (shiftTypes) => set((state) => ({ shiftTypes: typeof(shiftTypes) === "function" ? shiftTypes(state.shiftTypes) : shiftTypes})),
}));