export interface Patient {
  patient_id: string;
  name: string;
  age: number;
  gender: string;
  admission_date?: string;
  department?: string;
  document_count: number;
}

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: Source[];
}

export interface Source {
  source: string;
  section: string;
  score: number;
  text: string;
}

export interface Report {
  patient_id: string;
  patientInfo?: {
    name: string;
    age: number;
    gender: string;
    admissionDate?: string;
    dischargeDate?: string;
    lengthOfStay?: number;
    department?: string;
  };
  admissionReason?: string;
  diagnoses?: {
    primary: string;
    secondary: string[];
  };
  clinicalCourse?: string;
  therapy?: string;
  medications?: Array<{
    name: string;
    dose: string;
    frequency: string;
    indication: string;
  }>;
  labs?: {
    summary: string;
    notable: string[];
  };
  recommendations?: {
    followUp: string[];
    ambulatory: string[];
    lifestyle: string[];
  };
  [key: string]: any;
}
