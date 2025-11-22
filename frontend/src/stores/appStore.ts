import { create } from 'zustand';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  uploadedAt: string;
  status: 'uploading' | 'success' | 'error';
  progress: number;
}

export interface User {
  id: string;
  name: string;
  email: string;
  role: 'patient' | 'doctor' | 'admin';
  avatar?: string;
}

interface AppState {
  currentScreen: 'home' | 'dashboard' | 'upload' | 'about' | 'test';
  setCurrentScreen: (screen: AppState['currentScreen']) => void;
  user: User | null;
  isLoggedIn: boolean;
  login: (user: User) => void;
  logout: () => void;
  isChatOpen: boolean;
  toggleChat: () => void;
  messages: Message[];
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  clearMessages: () => void;
  uploadedFiles: UploadedFile[];
  addFile: (file: UploadedFile) => void;
  updateFileProgress: (id: string, progress: number) => void;
  updateFileStatus: (id: string, status: UploadedFile['status']) => void;
  removeFile: (id: string) => void;
  patientId: string;
}

export const useAppStore = create<AppState>((set) => ({
  currentScreen: 'home',
  setCurrentScreen: (screen) => set({ currentScreen: screen }),
  user: null,
  isLoggedIn: false,
  login: (user) => set({ user, isLoggedIn: true }),
  logout: () => set({ user: null, isLoggedIn: false }),
  isChatOpen: false,
  toggleChat: () => set((state) => ({ isChatOpen: !state.isChatOpen })),
  messages: [
    {
      id: '1',
      role: 'assistant',
      content: "👋 Hi! I'm MIMIQ, your medical AI assistant. How can I help you today?",
      timestamp: new Date().toISOString(),
    },
  ],
  addMessage: (message) =>
    set((state) => ({
      messages: [
        ...state.messages,
        {
          ...message,
          id: `msg_${Date.now()}`,
          timestamp: new Date().toISOString(),
        },
      ],
    })),
  clearMessages: () =>
    set({
      messages: [
        {
          id: '1',
          role: 'assistant',
          content: "👋 Hi! I'm MIMIQ, your medical AI assistant. How can I help you today?",
          timestamp: new Date().toISOString(),
        },
      ],
    }),
  uploadedFiles: [],
  addFile: (file) =>
    set((state) => ({ uploadedFiles: [...state.uploadedFiles, file] })),
  updateFileProgress: (id, progress) =>
    set((state) => ({
      uploadedFiles: state.uploadedFiles.map((f) =>
        f.id === id ? { ...f, progress } : f
      ),
    })),
  updateFileStatus: (id, status) =>
    set((state) => ({
      uploadedFiles: state.uploadedFiles.map((f) =>
        f.id === id ? { ...f, status } : f
      ),
    })),
  removeFile: (id) =>
    set((state) => ({
      uploadedFiles: state.uploadedFiles.filter((f) => f.id !== id),
    })),
  patientId: `patient_${Date.now()}`,
}));
