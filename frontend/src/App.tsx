import { useState, useEffect } from 'react';
import { Patient } from './types';
import { apiService } from './services/api.service';
import PatientList from './components/PatientList';
import ChatInterface from './components/ChatInterface';
import ReportGenerator from './components/ReportGenerator';
import ErrorBoundary from './components/ErrorBoundary';
import { FileText, MessageSquare, Activity } from 'lucide-react';

type View = 'chat' | 'report';

function App() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [view, setView] = useState<View>('chat');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPatients();
  }, []);

  const loadPatients = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getPatients();
      setPatients(data);

      // Auto-select first patient
      if (data.length > 0 && !selectedPatient) {
        setSelectedPatient(data[0]);
      }
    } catch (err) {
      console.error('Error loading patients:', err);
      setError('Fehler beim Laden der Patienten. Bitte stellen Sie sicher, dass alle Services laufen.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Activity className="w-8 h-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Semantic Patient File AI
                </h1>
                <p className="text-sm text-gray-600">
                  KI-gestützte Patientenakten-Analyse
                </p>
              </div>
            </div>

            {/* View Toggle */}
            <div className="flex space-x-2">
              <button
                onClick={() => setView('chat')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                  view === 'chat'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <MessageSquare className="w-4 h-4" />
                <span>Chat</span>
              </button>
              <button
                onClick={() => setView('report')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                  view === 'report'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <FileText className="w-4 h-4" />
                <span>Bericht</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
            <strong>Fehler:</strong> {error}
          </div>
        )}

        <div className="grid grid-cols-12 gap-6">
          {/* Patient List Sidebar */}
          <div className="col-span-12 lg:col-span-3">
            <PatientList
              patients={patients}
              selectedPatient={selectedPatient}
              onSelectPatient={setSelectedPatient}
              loading={loading}
            />
          </div>

          {/* Main View Area */}
          <div className="col-span-12 lg:col-span-9">
            {!selectedPatient && !loading ? (
              <div className="bg-white rounded-lg shadow-sm p-8 text-center">
                <Activity className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Wählen Sie einen Patienten
                </h3>
                <p className="text-gray-600">
                  Bitte wählen Sie einen Patienten aus der Liste links aus.
                </p>
              </div>
            ) : (
              <>
                {view === 'chat' && selectedPatient && (
                  <ChatInterface patient={selectedPatient} />
                )}
                {view === 'report' && selectedPatient && (
                  <ErrorBoundary>
                    <ReportGenerator patient={selectedPatient} />
                  </ErrorBoundary>
                )}
              </>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
