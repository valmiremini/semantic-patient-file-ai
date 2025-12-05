import { useState } from 'react';
import { Patient, Report } from '../types';
import { apiService } from '../services/api.service';
import { FileText, Loader2, Download, RefreshCw } from 'lucide-react';

interface ReportGeneratorProps {
  patient: Patient;
}

export default function ReportGenerator({ patient }: ReportGeneratorProps) {
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateReport = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiService.generateReport(patient.patient_id);
      console.log('Report response:', response);

      if (!response || !response.report) {
        throw new Error('Ungültige Antwort vom Server');
      }

      setReport(response.report);
    } catch (err) {
      console.error('Error generating report:', err);
      setError(err instanceof Error ? err.message : 'Fehler beim Generieren des Berichts');
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = () => {
    if (!report) return;

    const content = JSON.stringify(report, null, 2);
    const blob = new Blob([content], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `bericht_${patient.patient_id}_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="bg-white rounded-lg shadow-sm">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Bericht Generator</h2>
            <p className="text-sm text-gray-600">Patient: {patient.name}</p>
          </div>
          <div className="flex space-x-2">
            {report && (
              <button
                onClick={downloadReport}
                className="flex items-center space-x-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              >
                <Download className="w-4 h-4" />
                <span>Download</span>
              </button>
            )}
            <button
              onClick={generateReport}
              disabled={loading}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 transition-colors"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Generiere...</span>
                </>
              ) : (
                <>
                  <RefreshCw className="w-4 h-4" />
                  <span>Bericht generieren</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        {!report && !loading && (
          <div className="text-center py-12">
            <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Kein Bericht generiert
            </h3>
            <p className="text-gray-600 mb-6">
              Klicken Sie auf "Bericht generieren", um einen Entlassungsbericht zu erstellen.
            </p>
          </div>
        )}

        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
            {error}
          </div>
        )}

        {loading && (
          <div className="text-center py-12">
            <Loader2 className="w-16 h-16 text-blue-600 mx-auto mb-4 animate-spin" />
            <p className="text-gray-600">Bericht wird generiert...</p>
          </div>
        )}

        {report && !loading && (
          <div className="space-y-6">
            {/* Patient Info */}
            {report.patientInfo && (
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-3">Patienteninformationen</h3>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  {report.patientInfo.name && (
                    <div>
                      <span className="text-gray-600">Name:</span>
                      <p className="font-medium">{report.patientInfo.name}</p>
                    </div>
                  )}
                  {report.patientInfo.age && (
                    <div>
                      <span className="text-gray-600">Alter:</span>
                      <p className="font-medium">{report.patientInfo.age} Jahre</p>
                    </div>
                  )}
                  {report.patientInfo.gender && (
                    <div>
                      <span className="text-gray-600">Geschlecht:</span>
                      <p className="font-medium">{report.patientInfo.gender}</p>
                    </div>
                  )}
                  {report.patientInfo.department && (
                    <div>
                      <span className="text-gray-600">Abteilung:</span>
                      <p className="font-medium">{report.patientInfo.department}</p>
                    </div>
                  )}
                  {report.patientInfo.admissionDate && (
                    <div>
                      <span className="text-gray-600">Aufnahme:</span>
                      <p className="font-medium">
                        {new Date(report.patientInfo.admissionDate).toLocaleDateString('de-DE')}
                      </p>
                    </div>
                  )}
                  {report.patientInfo.dischargeDate && (
                    <div>
                      <span className="text-gray-600">Entlassung:</span>
                      <p className="font-medium">
                        {new Date(report.patientInfo.dischargeDate).toLocaleDateString('de-DE')}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Admission Reason */}
            {report.admissionReason && typeof report.admissionReason === 'string' && (
              <ReportSection title="Grund der Hospitalisation" content={report.admissionReason} />
            )}

            {/* Diagnoses */}
            {report.diagnoses && (
              <div className="border border-gray-200 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-3">Diagnosen</h3>
                <div className="space-y-2">
                  {report.diagnoses.primary && (
                    <div>
                      <span className="text-sm font-medium text-gray-600">Hauptdiagnose:</span>
                      <p className="text-sm">{report.diagnoses.primary}</p>
                    </div>
                  )}
                  {report.diagnoses.secondary && Array.isArray(report.diagnoses.secondary) && report.diagnoses.secondary.length > 0 && (
                    <div>
                      <span className="text-sm font-medium text-gray-600">Nebendiagnosen:</span>
                      <ul className="list-disc list-inside text-sm space-y-1">
                        {report.diagnoses.secondary.map((diag: string, idx: number) => (
                          <li key={idx}>{diag}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Clinical Course */}
            {report.clinicalCourse && typeof report.clinicalCourse === 'string' && (
              <ReportSection title="Klinischer Verlauf" content={report.clinicalCourse} />
            )}

            {/* Therapy */}
            {report.therapy && typeof report.therapy === 'string' && (
              <ReportSection title="Therapie" content={report.therapy} />
            )}

            {/* Medications */}
            {report.medications && Array.isArray(report.medications) && report.medications.length > 0 && (
              <div className="border border-gray-200 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-3">Medikation bei Entlassung</h3>
                <div className="space-y-3">
                  {report.medications.map((med: any, idx: number) => (
                    <div key={idx} className="text-sm bg-gray-50 p-3 rounded">
                      <p className="font-medium">{med?.name || 'N/A'} {med?.dose || ''}</p>
                      {med?.frequency && <p className="text-gray-600">Frequenz: {med.frequency}</p>}
                      {med?.indication && <p className="text-gray-600">Indikation: {med.indication}</p>}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Labs */}
            {report.labs && (
              <div className="border border-gray-200 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-3">Laborwerte</h3>
                {report.labs.summary && (
                  <p className="text-sm mb-3">{report.labs.summary}</p>
                )}
                {report.labs.notable && Array.isArray(report.labs.notable) && report.labs.notable.length > 0 && (
                  <div>
                    <span className="text-sm font-medium text-gray-600">Auffällige Werte:</span>
                    <ul className="list-disc list-inside text-sm space-y-1 mt-1">
                      {report.labs.notable.map((item: string, idx: number) => (
                        <li key={idx}>{item}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Recommendations */}
            {report.recommendations && (
              <div className="border border-gray-200 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-3">Empfehlungen</h3>
                <div className="space-y-3">
                  {report.recommendations.followUp && Array.isArray(report.recommendations.followUp) && report.recommendations.followUp.length > 0 && (
                    <div>
                      <span className="text-sm font-medium text-gray-600">Verlaufskontrolle:</span>
                      <ul className="list-disc list-inside text-sm space-y-1 mt-1">
                        {report.recommendations.followUp.map((item: string, idx: number) => (
                          <li key={idx}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {report.recommendations.ambulatory && Array.isArray(report.recommendations.ambulatory) && report.recommendations.ambulatory.length > 0 && (
                    <div>
                      <span className="text-sm font-medium text-gray-600">Ambulante Weiterbehandlung:</span>
                      <ul className="list-disc list-inside text-sm space-y-1 mt-1">
                        {report.recommendations.ambulatory.map((item: string, idx: number) => (
                          <li key={idx}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {report.recommendations.lifestyle && Array.isArray(report.recommendations.lifestyle) && report.recommendations.lifestyle.length > 0 && (
                    <div>
                      <span className="text-sm font-medium text-gray-600">Lebensstil:</span>
                      <ul className="list-disc list-inside text-sm space-y-1 mt-1">
                        {report.recommendations.lifestyle.map((item: string, idx: number) => (
                          <li key={idx}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function ReportSection({ title, content }: { title: string; content: any }) {
  // Handle non-string content
  const renderContent = () => {
    if (!content) return null;

    // If content is a string, render it normally
    if (typeof content === 'string') {
      return <p className="text-sm text-gray-700 whitespace-pre-wrap">{content}</p>;
    }

    // If content is an object, try to render it as JSON
    if (typeof content === 'object') {
      return (
        <pre className="text-sm text-gray-700 whitespace-pre-wrap bg-gray-50 p-3 rounded overflow-auto">
          {JSON.stringify(content, null, 2)}
        </pre>
      );
    }

    // Fallback: convert to string
    return <p className="text-sm text-gray-700">{String(content)}</p>;
  };

  return (
    <div className="border border-gray-200 rounded-lg p-4">
      <h3 className="font-semibold text-gray-900 mb-3">{title}</h3>
      {renderContent()}
    </div>
  );
}
