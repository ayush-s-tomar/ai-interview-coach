import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export const startSession = (role, difficulty = 'medium') =>
  api.post('/interview/start', { role, difficulty }).then(r => r.data)

export const transcribeAndScore = (sessionId, questionNumber, audioBlob) => {
  const form = new FormData()
  form.append('session_id', sessionId)
  form.append('question_number', questionNumber)
  form.append('audio', audioBlob, 'recording.webm')
  return api.post('/interview/transcribe-and-score', form).then(r => r.data)
}

export const getSummary = (sessionId, candidateName) =>
  api.get(`/interview/session/${sessionId}/summary`, { params: { candidate_name: candidateName } }).then(r => r.data)

export const speakText = async (text) => {
  const res = await api.post('/tts/speak', { text }, { responseType: 'blob' })
  return URL.createObjectURL(res.data)
}

export const downloadReport = (sessionId, candidateName) => {
  const url = `/api/report/generate/${sessionId}?candidate_name=${encodeURIComponent(candidateName)}`
  const a = document.createElement('a')
  a.href = url
  a.download = `interview_report.pdf`
  a.click()
}
