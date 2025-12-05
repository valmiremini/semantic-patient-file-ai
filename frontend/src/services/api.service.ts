import axios, { AxiosInstance } from 'axios';
import { Patient, Message, Report } from '../types';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    const baseURL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:3001';

    this.client = axios.create({
      baseURL: `${baseURL}/api`,
      timeout: 60000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    console.log('API Service initialized:', baseURL);
  }

  async getPatients(): Promise<Patient[]> {
    const response = await this.client.get<Patient[]>('/patients');
    return response.data;
  }

  async chat(
    patientId: string,
    question: string,
    conversationHistory: Array<{ role: string; content: string }> = []
  ): Promise<{ answer: string; sources: any[]; timestamp: string }> {
    const response = await this.client.post('/chat', {
      patient_id: patientId,
      question,
      conversation_history: conversationHistory,
    });
    return response.data;
  }

  async generateReport(patientId: string): Promise<{ report: Report; timestamp: string }> {
    // Report generation takes longer, use extended timeout
    const response = await this.client.post(
      '/reports/generate',
      {
        patient_id: patientId,
      },
      {
        timeout: 210000, // 210 seconds for report generation
      }
    );
    return response.data;
  }

  async uploadDocuments(patientId: string, files: File[]): Promise<any> {
    const formData = new FormData();
    formData.append('patient_id', patientId);

    files.forEach((file) => {
      formData.append('files', file);
    });

    const response = await this.client.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }
}

export const apiService = new ApiService();
