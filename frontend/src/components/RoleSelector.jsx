import React, { useState } from 'react'

const ROLES = [
  { id: 'SDE', label: 'Software Engineer', icon: '💻', desc: 'DSA, system design, backend fundamentals' },
  { id: 'AI Engineer', label: 'AI / ML Engineer', icon: '🤖', desc: 'ML concepts, LLMs, model evaluation' },
  { id: 'Data Analyst', label: 'Data Analyst', icon: '📊', desc: 'SQL, statistics, visualization, A/B testing' },
]

export default function RoleSelector({ onStart }) {
  const [selected, setSelected] = useState(null)
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(false)

  const handleStart = async () => {
    if (!selected) return
    setLoading(true)
    await onStart(selected, name || 'Candidate')
    setLoading(false)
  }

  return (
    <div style={{ maxWidth: 560, margin: '0 auto', padding: '60px 24px' }}>
      <div style={{ textAlign: 'center', marginBottom: 40 }}>
        <div style={{ fontSize: 48, marginBottom: 12 }}>🎙️</div>
        <h1 style={{ fontSize: 28, fontWeight: 700, color: '#f0f0ff' }}>AI Interview Coach</h1>
        <p style={{ color: '#8888aa', marginTop: 8 }}>
          Real-time voice interview simulator with AI scoring
        </p>
      </div>

      <div style={{ marginBottom: 20 }}>
        <label style={{ fontSize: 13, color: '#8888aa', display: 'block', marginBottom: 6 }}>
          Your Name (optional)
        </label>
        <input
          value={name}
          onChange={e => setName(e.target.value)}
          placeholder="Enter your name for the PDF report"
          style={{
            width: '100%', padding: '10px 14px', borderRadius: 8,
            background: '#1a1a2e', border: '1px solid #33336a',
            color: '#f0f0ff', fontSize: 14, outline: 'none'
          }}
        />
      </div>

      <div style={{ marginBottom: 28 }}>
        <label style={{ fontSize: 13, color: '#8888aa', display: 'block', marginBottom: 10 }}>
          Select Your Role
        </label>
        {ROLES.map(role => (
          <div
            key={role.id}
            onClick={() => setSelected(role.id)}
            style={{
              padding: '14px 18px', borderRadius: 10, marginBottom: 10, cursor: 'pointer',
              border: `2px solid ${selected === role.id ? '#6c63ff' : '#33336a'}`,
              background: selected === role.id ? '#1e1e40' : '#1a1a2e',
              transition: 'all 0.2s',
              display: 'flex', alignItems: 'center', gap: 14
            }}
          >
            <span style={{ fontSize: 24 }}>{role.icon}</span>
            <div>
              <div style={{ fontWeight: 600, fontSize: 14 }}>{role.label}</div>
              <div style={{ fontSize: 12, color: '#8888aa', marginTop: 2 }}>{role.desc}</div>
            </div>
            {selected === role.id && (
              <span style={{ marginLeft: 'auto', color: '#6c63ff', fontSize: 18 }}>✓</span>
            )}
          </div>
        ))}
      </div>

      <button
        onClick={handleStart}
        disabled={!selected || loading}
        style={{
          width: '100%', padding: '14px', borderRadius: 10,
          background: selected ? '#6c63ff' : '#33336a',
          color: '#fff', border: 'none', fontSize: 15, fontWeight: 600,
          transition: 'all 0.2s', opacity: loading ? 0.7 : 1
        }}
      >
        {loading ? 'Starting...' : '🚀 Start Interview'}
      </button>
    </div>
  )
}
