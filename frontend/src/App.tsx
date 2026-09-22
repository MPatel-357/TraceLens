import { useEffect, useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000";

type Summary = {
  total_logs: number;
  level_counts: Record<string, number>;
  service_counts: Record<string, number>;
  problem_rate_percent: number;
};

type Anomaly = {
  timestamp: string;
  total_logs: number;
  errors: number;
  warnings: number;
  error_rate: number;
  anomaly_score: number;
};

type Analysis = {
  summary: string;
  likely_cause: string;
  evidence: string[];
  affected_services: string[];
  recommended_checks: string[];
  confidence: string;
};

function App() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [selectedTimestamp, setSelectedTimestamp] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [summaryResponse, anomalyResponse] = await Promise.all([
          fetch(`${API}/analytics/summary`),
          fetch(`${API}/analytics/anomalies`),
        ]);

        if (!summaryResponse.ok || !anomalyResponse.ok) {
          throw new Error("Unable to load TraceLens data.");
        }

        const summaryData = await summaryResponse.json();
        const anomalyData = await anomalyResponse.json();

        setSummary(summaryData);
        setAnomalies(anomalyData.anomalies);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Unable to load dashboard."
        );
      }
    }

    loadDashboard();
  }, []);

  async function investigate(timestamp: string) {
    setLoading(true);
    setAnalysis(null);
    setSelectedTimestamp(timestamp);
    setError("");

    try {
      const response = await fetch(
        `${API}/incidents/analyze?timestamp=${encodeURIComponent(timestamp)}`
      );

      if (!response.ok) {
        throw new Error("Incident analysis failed.");
      }

      const data = await response.json();
      setAnalysis(data.analysis);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Incident analysis failed."
      );
    } finally {
      setLoading(false);
    }
  }

  const errorCount =
    (summary?.level_counts.ERROR ?? 0) +
    (summary?.level_counts.CRITICAL ?? 0);

  return (
    <main className="dashboard">
      <header>
        <div>
          <div className="brand">TRACELENS</div>
          <h1>Production Intelligence</h1>
          <p>
            ML-powered anomaly detection with evidence-grounded AI incident
            analysis.
          </p>
        </div>

        <div className="status">
          <span className="status-dot" />
          SYSTEM LIVE
        </div>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <section className="metrics">
        <Metric
          label="TOTAL LOGS"
          value={summary?.total_logs.toLocaleString() ?? "—"}
        />
        <Metric label="ERRORS" value={errorCount.toLocaleString()} />
        <Metric
          label="PROBLEM RATE"
          value={
            summary ? `${summary.problem_rate_percent.toFixed(2)}%` : "—"
          }
        />
        <Metric label="ANOMALIES" value={anomalies.length.toString()} />
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <span className="eyebrow">ISOLATION FOREST</span>
            <h2>Detected Anomalies</h2>
          </div>
          <span className="count">{anomalies.length} detected</span>
        </div>

        <div className="anomaly-list">
          {anomalies.map((anomaly) => (
            <article className="anomaly" key={anomaly.timestamp}>
              <div className="anomaly-main">
                <div className="anomaly-time">
                  {new Date(anomaly.timestamp).toLocaleString()}
                </div>

                <div className="anomaly-stats">
                  <span>{anomaly.total_logs} logs</span>
                  <span>{anomaly.errors} errors</span>
                  <span>{anomaly.warnings} warnings</span>
                  <span>
                    {(anomaly.error_rate * 100).toFixed(1)}% error rate
                  </span>
                </div>
              </div>

              <div className="anomaly-actions">
                <span className="score">
                  score {anomaly.anomaly_score.toFixed(4)}
                </span>

                <button onClick={() => investigate(anomaly.timestamp)}>
                  Investigate
                </button>
              </div>
            </article>
          ))}

          {!anomalies.length && (
            <div className="empty">No anomalies detected.</div>
          )}
        </div>
      </section>

      <section className="panel analysis-panel">
        <div className="panel-heading">
          <div>
            <span className="eyebrow">GENERATIVE AI</span>
            <h2>Incident Analysis</h2>
          </div>

          {analysis && (
            <span className={`confidence ${analysis.confidence.toLowerCase()}`}>
              {analysis.confidence} confidence
            </span>
          )}
        </div>

        {loading && (
          <div className="empty">
            Analyzing incident evidence...
          </div>
        )}

        {!loading && !analysis && (
          <div className="empty">
            Select an anomaly above to generate an evidence-grounded incident
            analysis.
          </div>
        )}

        {analysis && !loading && (
          <div className="analysis">
            <div className="analysis-summary">
              <span className="eyebrow">INCIDENT</span>
              <p>{analysis.summary}</p>

              <span className="eyebrow">LIKELY CAUSE</span>
              <p>{analysis.likely_cause}</p>

              <div className="timestamp">
                Window: {new Date(selectedTimestamp).toLocaleString()}
              </div>
            </div>

            <div className="analysis-grid">
              <div>
                <h3>Evidence</h3>
                <ul>
                  {analysis.evidence.map((item, index) => (
                    <li key={index}>{item}</li>
                  ))}
                </ul>
              </div>

              <div>
                <h3>Recommended Checks</h3>
                <ul>
                  {analysis.recommended_checks.map((item, index) => (
                    <li key={index}>{item}</li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="services">
              <span>IMPACTED SERVICES</span>
              {analysis.affected_services.map((service) => (
                <strong key={service}>{service}</strong>
              ))}
            </div>
          </div>
        )}
      </section>

      <footer>
        TraceLens · FastAPI · React · Isolation Forest · Generative AI
      </footer>
    </main>
  );
}

function Metric({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <article className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

export default App;