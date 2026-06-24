import React from 'react'

const DIM_COLORS = {
  relevance: '#6c63ff',
  clarity: '#22c55e',
  technical_accuracy: '#f59e0b',
  confidence: '#a78bfa',
}

function ScoreBar({ label, value, color }) {
  const pct = (value / 10) * 100
  return (
    <div style={{ marginBottom: 10 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
        <span style={{ fontSize: 12, color: '#aaa', textTransform: 'capitalize' }}>
          {label.replace('_', ' ')}
        </span>
        <span style={{ fontSize: 13, fontWeight: 600, color }}>{value.toFixed(1)}/10</span>
      </div>
      <div style={{ height: 6, background: '#2a2a4a', borderRadius: 3, overflow: 'hidden' }}>
        <div style={{
          height: '100%', width: `${pct}%`, background: color,
          borderRadius: 3, transition: 'width 0.8s ease'
        }} />
      </div>
    </div>
  )
}

export default function ScoreCard({ score, questionNum, question }) {
  if (!score) return null
  const dims = ['relevance', 'clarity', 'technical_accuracy', 'confidence']

  return (
    <div style={{
      background: '#1a1a2e', border: '1px solid #33336a', borderRadius: 12,
      padding: 20, marginTop: 16
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
        <span style={{ fontWeight: 600, fontSize: 14 }}>Q{questionNum} Score</span>
        <span style={{
          fontSize: 20, fontWeight: 700,
          color: score.overall >= 7 ? '#22c55e' : score.overall >= 5 ? '#f59e0b' : '#ef4444'
        }}>
          {score.overall.toFixed(1)}/10
        </span>
      </div>

      {dims.map(d => (
        <ScoreBar key={d} label={d} value={score[d]} color={DIM_COLORS[d]} />
      ))}

      <div style={{
        background: '#0f0f1a', borderRadius: 8, padding: 12, marginTop: 12,
        fontSize: 13, lineHeight: 1.6, color: '#ccc'
      }}>
        <strong style={{ color: '#a78bfa' }}>Feedback:</strong> {score.feedback}
      </div>

      {score.improvement_tips?.length > 0 && (
        <div style={{ marginTop: 10 }}>
          <div style={{ fontSize: 12, color: '#888', marginBottom: 6 }}>💡 Tips to improve:</div>
          {score.improvement_tips.map((tip, i) => (
            <div key={i} style={{ fontSize: 12, color: '#bbb', marginBottom: 4 }}>• {tip}</div>
          ))}
        </div>
      )}
    </div>
  )
}
