import React, { useState, useEffect, useRef } from 'react'
import { useRecorder } from '../hooks/useRecorder'
import { transcribeAndScore, speakText, downloadReport } from '../utils/api'
import ScoreCard from './ScoreCard'

export default function InterviewRoom({ session, candidateName }) {
  const { session_id, role, total_questions, first_question } = session
  const [currentQuestion, setCurrentQuestion] = useState(first_question)
  const [questionNum, setQuestionNum] = useState(1)
  const [scores, setScores] = useState([])
  const [transcripts, setTranscripts] = useState([])
  const [status, setStatus] = useState('idle') // idle | speaking | recording | processing | done
  const [latestScore, setLatestScore] = useState(null)
  const [showScore, setShowScore] = useState(false)
  const [audioPlaying, setAudioPlaying] = useState(false)
  const audioRef = useRef(null)

  const { isRecording, audioBlob, startRecording, stopRecording } = useRecorder()

  // Auto-speak when question changes
  useEffect(() => {
    if (currentQuestion && status !== 'done') {
      speakQuestion(currentQuestion)
    }
  }, [currentQuestion])

  // Auto-submit when recording stops
  useEffect(() => {
    if (audioBlob && !isRecording) {
      handleSubmitAnswer(audioBlob)
    }
  }, [audioBlob])

  const speakQuestion = async (text) => {
    setStatus('speaking')
    setAudioPlaying(true)
    try {
      const url = await speakText(text)
      const audio = new Audio(url)
      audioRef.current = audio
      audio.onended = () => {
        setAudioPlaying(false)
        setStatus('idle')
      }
      audio.play()
    } catch {
      setAudioPlaying(false)
      setStatus('idle')
    }
  }

  const handleRecord = () => {
    if (isRecording) {
      stopRecording()
      setStatus('processing')
    } else {
      if (audioRef.current) audioRef.current.pause()
      setStatus('recording')
      startRecording()
    }
  }

  const handleSubmitAnswer = async (blob) => {
    setStatus('processing')
    setShowScore(false)
    try {
      const result = await transcribeAndScore(session_id, questionNum, blob)
      setLatestScore(result.score)
      setScores(prev => [...prev, result.score])
      setTranscripts(prev => [...prev, result.transcript])
      setShowScore(true)

      if (result.is_complete) {
        setStatus('done')
      } else {
        setTimeout(() => {
          setShowScore(false)
          setQuestionNum(questionNum + 1)
          setCurrentQuestion(result.next_question)
          setStatus('idle')
        }, 6000)
      }
    } catch (e) {
      alert('Error processing answer: ' + (e.response?.data?.detail || e.message))
      setStatus('idle')
    }
  }

  const avgScore = scores.length
    ? (scores.reduce((a, b) => a + b.overall, 0) / scores.length).toFixed(1)
    : null

  const progress = ((questionNum - 1) / total_questions) * 100

  const statusText = {
    idle: '🎙️ Click to answer',
    speaking: '🔊 Listen to the question...',
    recording: '🔴 Recording... Click to stop',
    processing: '⏳ Analyzing your answer...',
    done: '✅ Interview complete!',
  }

  return (
    <div style={{ maxWidth: 640, margin: '0 auto', padding: '32px 24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <span style={{ fontSize: 12, color: '#8888aa' }}>{role} Interview</span>
          <div style={{ fontWeight: 700, fontSize: 16 }}>
            {candidateName}
          </div>
        </div>
        {avgScore && (
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: 11, color: '#8888aa' }}>Avg Score</div>
            <div style={{ fontSize: 22, fontWeight: 700, color: '#6c63ff' }}>{avgScore}/10</div>
          </div>
        )}
      </div>

      {/* Progress bar */}
      <div style={{ height: 4, background: '#2a2a4a', borderRadius: 2, marginBottom: 28 }}>
        <div style={{
          height: '100%', width: `${progress}%`, background: '#6c63ff',
          borderRadius: 2, transition: 'width 0.5s'
        }} />
      </div>

      {/* Question card */}
      <div style={{
        background: '#1a1a2e', border: '1px solid #33336a', borderRadius: 14,
        padding: 24, marginBottom: 20
      }}>
        <div style={{ fontSize: 12, color: '#6c63ff', fontWeight: 600, marginBottom: 10 }}>
          QUESTION {questionNum} OF {total_questions}
        </div>
        <div style={{ fontSize: 18, fontWeight: 500, lineHeight: 1.6 }}>
          {currentQuestion}
        </div>
      </div>

      {/* Status */}
      <div style={{
        textAlign: 'center', padding: '10px', marginBottom: 16,
        fontSize: 13, color: status === 'recording' ? '#ef4444' : '#8888aa'
      }}>
        {statusText[status]}
      </div>

      {/* Record button */}
      {status !== 'done' && (
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <button
            onClick={handleRecord}
            disabled={status === 'processing' || status === 'speaking'}
            style={{
              width: 80, height: 80, borderRadius: '50%',
              border: `3px solid ${isRecording ? '#ef4444' : '#6c63ff'}`,
              background: isRecording ? '#ef4444' : '#6c63ff',
              color: '#fff', fontSize: 28,
              boxShadow: isRecording ? '0 0 0 8px rgba(239,68,68,0.2)' : '0 0 0 8px rgba(108,99,255,0.15)',
              transition: 'all 0.2s',
              display: 'inline-flex', alignItems: 'center', justifyContent: 'center'
            }}
          >
            {isRecording ? '⏹' : '🎙️'}
          </button>
          <div style={{ fontSize: 11, color: '#666', marginTop: 8 }}>
            {isRecording ? 'Tap to stop' : 'Tap to record'}
          </div>
        </div>
      )}

      {/* Score card */}
      {showScore && latestScore && (
        <ScoreCard score={latestScore} questionNum={questionNum} />
      )}

      {/* Done state */}
      {status === 'done' && (
        <div style={{
          textAlign: 'center', background: '#1a1a2e', border: '1px solid #33336a',
          borderRadius: 14, padding: 32
        }}>
          <div style={{ fontSize: 40, marginBottom: 12 }}>🎉</div>
          <h2 style={{ fontSize: 20, marginBottom: 8 }}>Interview Complete!</h2>
          <div style={{ color: '#8888aa', marginBottom: 8 }}>
            Final Average Score:
            <span style={{
              fontSize: 32, fontWeight: 700, display: 'block',
              color: avgScore >= 7 ? '#22c55e' : avgScore >= 5 ? '#f59e0b' : '#ef4444'
            }}>
              {avgScore}/10
            </span>
          </div>
          <div style={{ color: '#888', fontSize: 13, marginBottom: 24 }}>
            {scores.length} question{scores.length !== 1 ? 's' : ''} answered
          </div>
          <button
            onClick={() => downloadReport(session_id, candidateName)}
            style={{
              background: '#6c63ff', color: '#fff', border: 'none',
              borderRadius: 10, padding: '12px 28px', fontSize: 14, fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            📄 Download PDF Report
          </button>
        </div>
      )}
    </div>
  )
}
