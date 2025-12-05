import axios, { AxiosInstance } from 'axios';

export interface ChatRequest {
  patient_id: string;
  question: string;
  conversation_history?: Array<{ role: string; content: string }>;
}

export interface ChatResponse {
  answer: string;
  sources: Array<{
    source: string;
    section: string;
    score: number;
    text: string;
  }>;
  timestamp: string;
}

export interface ReportRequest {
  patient_id: string;
}

export interface ReportResponse {
  report: any;
  timestamp: string;
}

export interface PatientInfo {
  patient_id: string;
  name: string;
  age: number;
  gender: string;
  admission_date?: string;
  department?: string;
  document_count: number;
}

class AIService {
  private client: AxiosInstance;

  constructor() {
    const baseURL = process.env.AI_SERVICE_URL || 'http://ai-service:8000';

    this.client = axios.create({
      baseURL,
      timeout: 60000, // 60 seconds
      headers: {
        'Content-Type': 'application/json',
      },
    });

    console.log(`🤖 AI Service client initialized: ${baseURL}`);
  }

  async getPatients(): Promise<PatientInfo[]> {
    try {
      const response = await this.client.get<PatientInfo[]>('/patients');
      return response.data;
    } catch (error) {
      console.error('Error fetching patients:', error);
      throw new Error('Failed to fetch patients from AI service');
    }
  }

  async chat(request: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await this.client.post<ChatResponse>('/chat', request);
      return response.data;
    } catch (error) {
      console.error('Error in chat:', error);
      throw new Error('Failed to get chat response from AI service');
    }
  }

  async generateReport(request: ReportRequest): Promise<ReportResponse> {
    try {
      // Report generation takes longer, use extended timeout
      const response = await this.client.post<ReportResponse>(
        '/generate-report',
        request,
        {
          timeout: 200000, // 200 seconds for report generation
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error generating report:', error);
      throw new Error('Failed to generate report from AI service');
    }
  }

  async uploadDocuments(patientId: string, files: Express.Multer.File[]): Promise<any> {
    try {
      const formData = new FormData();

      // Add files to form data
      for (const file of files) {
        const blob = new Blob([file.buffer], { type: file.mimetype });
        formData.append('files', blob, file.originalname);
      }

      const response = await this.client.post(
        `/upload?patient_id=${patientId}`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      return response.data;
    } catch (error) {
      console.error('Error uploading documents:', error);
      throw new Error('Failed to upload documents to AI service');
    }
  }

  async healthCheck(): Promise<boolean> {
    try {
      const response = await this.client.get('/health');
      return response.status === 200;
    } catch (error) {
      return false;
    }
  }
}

export const aiService = new AIService();
