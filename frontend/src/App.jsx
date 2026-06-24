import React, { useState } from 'react'
import RoleSelector from './components/RoleSelector'
import InterviewRoom from './components/InterviewRoom'
import { startSession } from './utils/api'

export default function App() {
  const [session, setSession] = useState(null)
  const [candidateName, setCandidateName] = useState('Candidate')
  const [error, setError] = useState(null)

  const handleStart = async (role, name) => {
    try {
      setError(null)
      const data = await startSession(role)
      setCandidateName(name)
      setSession(data)
    } catch (e) {
      setError('Failed to connect to backend. Make sure the API server is running on port 8000.')
      console.error(e)
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: '#0f0f1a' }}>
      {error && (
        <div style={{
          background: '#2a1a1a', borderBottom: '1px solid #ef4444',
          padding: '12px 24px', fontSize: 13, color: '#fca5a5', textAlign: 'center'
        }}>
          ⚠️ {error}
        </div>
      )}

      {!session ? (
        <RoleSelector onStart={handleStart} />
      ) : (
        <InterviewRoom session={session} candidateName={candidateName} />
      )}
    </div>
  )
}
