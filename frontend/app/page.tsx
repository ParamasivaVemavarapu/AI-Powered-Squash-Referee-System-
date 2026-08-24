"use client";

import { FormEvent, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Decision = {
  decision: string;
  confidence: number;
  human_review_required: boolean;
  reason: string;
  evidence: string[];
};

type Flags = {
  ball_hit_tin: boolean;
  ball_out: boolean;
  double_bounce: boolean;
  interference: boolean;
  direct_access: boolean;
  prevented_swing: boolean;
  safety_risk: boolean;
};

const initialFlags: Flags = {
  ball_hit_tin: false,
  ball_out: false,
  double_bounce: false,
  interference: false,
  direct_access: true,
  prevented_swing: false,
  safety_risk: false,
};

export default function Home() {
  const [flags, setFlags] = useState(initialFlags);
  const [confidence, setConfidence] = useState(0.94);
  const [result, setResult] = useState<Decision | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function toggle(key: keyof Flags) {
    setFlags((current) => ({ ...current, [key]: !current[key] }));
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`${API_URL}/api/v1/decisions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          rally_id: `rally-${Date.now()}`,
          ball_hit_tin: flags.ball_hit_tin,
          ball_out: flags.ball_out,
          bounce_count: flags.double_bounce ? 2 : 0,
          interference: flags.interference,
          striker_had_direct_access: flags.direct_access,
          opponent_prevented_swing: flags.prevented_swing,
          safety_risk: flags.safety_risk,
          observation_confidence: confidence,
        }),
      });
      if (!response.ok) throw new Error("Decision service returned an error.");
      setResult(await response.json());
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Request failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <nav>
        <div className="brand"><span>CS</span> COURTSENSE</div>
        <div className="live"><i /> REFEREE CONSOLE</div>
      </nav>

      <header>
        <p className="eyebrow">EXPLAINABLE DECISION SUPPORT</p>
        <h1>Every call.<br /><em>Evidence included.</em></h1>
        <p className="lede">
          Convert rally observations into transparent squash decisions with
          confidence-aware human escalation.
        </p>
      </header>

      <section className="workspace">
        <form onSubmit={submit}>
          <div className="section-label">
            <span>01</span>
            <div><strong>Rally observation</strong><small>Select every observed condition</small></div>
          </div>
          <div className="flags">
            {([
              ["ball_hit_tin", "Tin contact"],
              ["ball_out", "Ball out"],
              ["double_bounce", "Double bounce"],
              ["interference", "Interference"],
              ["direct_access", "Direct access"],
              ["prevented_swing", "Swing prevented"],
              ["safety_risk", "Safety risk"],
            ] as [keyof Flags, string][]).map(([key, label]) => (
              <button
                type="button"
                className={flags[key] ? "active" : ""}
                onClick={() => toggle(key)}
                key={key}
              >
                <b>{flags[key] ? "✓" : "+"}</b>{label}
              </button>
            ))}
          </div>

          <label className="confidence">
            <span>Observation confidence <strong>{Math.round(confidence * 100)}%</strong></span>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={confidence}
              onChange={(e) => setConfidence(Number(e.target.value))}
            />
          </label>

          <button className="submit" disabled={loading}>
            {loading ? "Evaluating…" : "Evaluate rally →"}
          </button>
          {error && <p className="error">{error}</p>}
        </form>

        <aside className={result ? "result populated" : "result"}>
          <div className="section-label">
            <span>02</span>
            <div><strong>Referee decision</strong><small>Rules, evidence, confidence</small></div>
          </div>
          {!result ? (
            <div className="empty">
              <div className="court"><i /><i /><i /></div>
              <p>Submit a rally observation<br />to generate an explainable call.</p>
            </div>
          ) : (
            <div className="decision">
              <p className="eyebrow">{result.human_review_required ? "ESCALATED" : "AUTOMATED CALL"}</p>
              <h2>{result.decision.replaceAll("_", " ")}</h2>
              <div className="score">{Math.round(result.confidence * 100)}% confidence</div>
              <p>{result.reason}</p>
              <ul>
                {result.evidence.map((item) => <li key={item}>{item.replaceAll("_", " ")}</li>)}
              </ul>
            </div>
          )}
        </aside>
      </section>

      <footer>
        <span>FastAPI · Next.js · TypeScript</span>
        <span>Decision support — human officials retain authority</span>
      </footer>
    </main>
  );
}
