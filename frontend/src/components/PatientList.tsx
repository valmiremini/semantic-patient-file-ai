import { Patient } from '../types';
import { User, Calendar, Building2, FileText } from 'lucide-react';

interface PatientListProps {
  patients: Patient[];
  selectedPatient: Patient | null;
  onSelectPatient: (patient: Patient) => void;
  loading: boolean;
}

export default function PatientList({
  patients,
  selectedPatient,
  onSelectPatient,
  loading,
}: PatientListProps) {
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-lg font-semibold mb-4">Patienten</h2>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="animate-pulse">
              <div className="h-20 bg-gray-200 rounded-lg"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (patients.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-lg font-semibold mb-4">Patienten</h2>
        <p className="text-gray-600 text-sm">Keine Patienten gefunden.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm p-4">
      <h2 className="text-lg font-semibold mb-4 px-2">Patienten</h2>
      <div className="space-y-2">
        {patients.map((patient) => (
          <button
            key={patient.patient_id}
            onClick={() => onSelectPatient(patient)}
            className={`w-full text-left p-3 rounded-lg transition-colors ${
              selectedPatient?.patient_id === patient.patient_id
                ? 'bg-blue-50 border-2 border-blue-500'
                : 'bg-gray-50 border-2 border-transparent hover:bg-gray-100'
            }`}
          >
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                  <User className="w-5 h-5 text-blue-600" />
                </div>
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-gray-900 truncate">{patient.name}</p>
                <p className="text-xs text-gray-500">
                  {patient.age} Jahre • {patient.gender}
                </p>
                {patient.department && (
                  <div className="flex items-center space-x-1 mt-1">
                    <Building2 className="w-3 h-3 text-gray-400" />
                    <p className="text-xs text-gray-600">{patient.department}</p>
                  </div>
                )}
                <div className="flex items-center space-x-1 mt-1">
                  <FileText className="w-3 h-3 text-gray-400" />
                  <p className="text-xs text-gray-600">
                    {patient.document_count} Dokumente
                  </p>
                </div>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
