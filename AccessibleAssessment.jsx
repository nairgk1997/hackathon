import { useState, useEffect, useCallback, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Volume2, Mic, ChevronRight, ChevronLeft,
  CheckCircle, AlertCircle, Loader2,
} from 'lucide-react'
import api from '../api/client'
import AudioRecorder from '../components/AudioRecorder'

// ── Text-to-Speech helper ─────────────────────────────────────────────────────

function speak(text) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const utt   = new SpeechSynthesisUtterance(text)
  utt.rate    = 0.88
  utt.pitch   = 1
  utt.lang    = 'en-US'
  window.speechSynthesis.speak(utt)
}

// ── Component ─────────────────────────────────────────────────────────────────

export default function AccessibleAssessment() {
  const navigate = useNavigate()

  const [phase, setPhase]         = useState('loading')   // loading|questions|submitting|done|error
  const [questions, setQuestions] = useState([])
  const [answers, setAnswers]     = useState({})           // { [questionId]: string }
  const [currentIdx, setCurrentIdx] = useState(0)
  const [liveMsg, setLiveMsg]     = useState('')           // aria-live region
  const [result, setResult]       = useState(null)
  const [errorMsg, setErrorMsg]   = useState('')

  const mainRef    = useRef(null)
  const headingRef = useRef(null)

  // ── aria-live: double-set to reliably trigger screen readers ─────────────────
  const announce = useCallback((msg) => {
    setLiveMsg('')
    setTimeout(() => setLiveMsg(msg), 60)
  }, [])

  // ── Fetch questions on mount ──────────────────────────────────────────────────
  useEffect(() => {
    const token = localStorage.getItem('candidate_token')
    announce('Loading your accessible assessment. Please wait.')

    api
      .get('/accessible-assessment/start', {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((res) => {
        setQuestions(res.data.questions)
        setPhase('questions')
        announce(
          `Assessment ready. ${res.data.questions.length} questions to complete. ` +
          'There is no time limit. Questions will be read aloud automatically.'
        )
      })
      .catch(() => {
        setPhase('error')
        setErrorMsg('Failed to load your assessment. Please refresh the page.')
        announce('Error: could not load assessment. Please refresh the page.')
      })
  }, [])

  // ── Auto-speak whenever the visible question changes ─────────────────────────
  const currentQ = questions[currentIdx]

  useEffect(() => {
    if (phase !== 'questions' || !currentQ) return

    let text = `Question ${currentIdx + 1} of ${questions.length}. ${currentQ.question}`
    if (currentQ.type === 'mcq' && currentQ.options) {
      text += '. The options are: ' + currentQ.options.join('. ')
    }
    speak(text)

    // Move browser focus to the question heading so Tab starts from there
    setTimeout(() => headingRef.current?.focus(), 100)
  }, [currentIdx, phase])

  // ── Answer helpers ────────────────────────────────────────────────────────────
  const setAnswer = (qid, value) =>
    setAnswers((prev) => ({ ...prev, [qid]: value }))

  // ── Navigation ────────────────────────────────────────────────────────────────
  const goNext = useCallback(() => {
    if (currentIdx < questions.length - 1) setCurrentIdx((i) => i + 1)
  }, [currentIdx, questions.length])

  const goPrev = useCallback(() => {
    if (currentIdx > 0) setCurrentIdx((i) => i - 1)
  }, [currentIdx])

  // Arrow-key navigation — only when focus is not inside a text field
  useEffect(() => {
    const handler = (e) => {
      if (phase !== 'questions') return
      const tag = document.activeElement?.tagName
      if (['INPUT', 'TEXTAREA', 'SELECT'].includes(tag)) return
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') { e.preventDefault(); goNext() }
      if (e.key === 'ArrowLeft'  || e.key === 'ArrowUp')   { e.preventDefault(); goPrev() }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [phase, goNext, goPrev])

  // ── Submit ────────────────────────────────────────────────────────────────────
  const handleSubmit = async () => {
    setPhase('submitting')
    announce('Submitting your answers. Please wait while our evaluator reviews them.')

    const token   = localStorage.getItem('candidate_token')
    const payload = questions.map((q) => ({
      question_id: q.id,
      question:    q.question,
      answer:      answers[q.id] || '',
    }))

    try {
      const res = await api.post(
        '/accessible-assessment/submit',
        { answers: payload },
        { headers: { Authorization: `Bearer ${token}` } },
      )
      setResult(res.data)
      setPhase('done')
      localStorage.setItem('assessment_result', JSON.stringify(res.data))

      const scoreMsg =
        `Assessment complete. Your technical score is ${res.data.technical_score} out of 100. ` +
        res.data.reasoning_summary
      speak(scoreMsg)
      announce(scoreMsg)
    } catch {
      setPhase('error')
      setErrorMsg('Submission failed. Please check your connection and try again.')
      announce('Submission failed. Please try again.')
    }
  }

  const answeredCount = questions.filter((q) => answers[q.id]?.trim()).length

  // ── Shared focus-ring class used on every interactive element ─────────────────
  const focusRing =
    'focus:outline-none focus:ring-4 focus:ring-sky-400 focus:ring-offset-2 focus:ring-offset-slate-950'

  // ── Render ────────────────────────────────────────────────────────────────────
  return (
    <div
      className="min-h-screen bg-slate-950 text-white font-sans"
      role="application"
      aria-label="Accessible Technical Assessment"
    >
      {/* ── ARIA live region — always in DOM, screen readers watch it ── */}
      <div
        role="status"
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
      >
        {liveMsg}
      </div>

      {/* ── Skip link ── */}
      <a
        href="#main-content"
        className={
          'sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-50 ' +
          'focus:px-4 focus:py-2 focus:bg-sky-600 focus:text-white focus:rounded-lg focus:font-bold ' +
          focusRing
        }
      >
        Skip to main content
      </a>

      {/* ── Header ── */}
      <header
        className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-sm sticky top-0 z-40"
        role="banner"
      >
        <div className="max-w-3xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-lg font-bold text-white">Accessible Assessment</h1>
            <p className="text-xs text-slate-400 mt-0.5">
              Audio-optimised · No time limit · Keyboard navigable
            </p>
          </div>
          {phase === 'questions' && (
            <div
              className="text-sm font-semibold text-sky-400"
              aria-label={`${answeredCount} of ${questions.length} questions answered`}
              aria-live="polite"
            >
              {answeredCount} / {questions.length} answered
            </div>
          )}
        </div>
      </header>

      {/* ── Main ── */}
      <main
        id="main-content"
        ref={mainRef}
        tabIndex={-1}
        className="outline-none max-w-3xl mx-auto px-6 py-10"
      >

        {/* Loading */}
        {phase === 'loading' && (
          <div
            className="flex flex-col items-center justify-center min-h-[55vh] gap-5"
            role="status"
            aria-label="Loading assessment"
          >
            <Loader2 size={44} className="text-sky-400 animate-spin" aria-hidden="true" />
            <p className="text-slate-300 text-xl font-semibold">Loading your assessment…</p>
            <p className="text-slate-500 text-sm">Questions will be read aloud automatically when ready.</p>
          </div>
        )}

        {/* Error */}
        {phase === 'error' && (
          <div
            className="flex flex-col items-center justify-center min-h-[55vh] gap-5"
            role="alert"
          >
            <AlertCircle size={44} className="text-red-400" aria-hidden="true" />
            <p className="text-red-300 text-xl font-semibold">{errorMsg}</p>
            <button
              onClick={() => window.location.reload()}
              className={`px-6 py-3 bg-red-600 hover:bg-red-500 text-white font-bold rounded-xl transition-colors ${focusRing} focus:ring-red-400`}
            >
              Reload page
            </button>
          </div>
        )}

        {/* Questions */}
        {phase === 'questions' && currentQ && (
          <>
            {/* Progress bar */}
            <div
              role="progressbar"
              aria-valuenow={currentIdx + 1}
              aria-valuemin={1}
              aria-valuemax={questions.length}
              aria-label={`Question ${currentIdx + 1} of ${questions.length}`}
              className="w-full bg-slate-800 rounded-full h-2 mb-10"
            >
              <div
                className="bg-sky-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${((currentIdx + 1) / questions.length) * 100}%` }}
              />
            </div>

            {/* Question card */}
            <section
              aria-labelledby="question-heading"
              className="bg-slate-900 border border-slate-700 rounded-2xl p-8 mb-6"
            >
              {/* Card header row */}
              <div className="flex items-center justify-between mb-6">
                <span
                  className="text-xs font-bold text-sky-400 uppercase tracking-widest"
                  aria-hidden="true"
                >
                  Question {currentIdx + 1} of {questions.length}
                </span>
                <button
                  onClick={() => {
                    let text = currentQ.question
                    if (currentQ.type === 'mcq' && currentQ.options)
                      text += '. Options: ' + currentQ.options.join('. ')
                    speak(text)
                  }}
                  className={`flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-sky-300 px-3 py-1.5 rounded-lg border border-slate-700 hover:border-sky-600 transition-all ${focusRing}`}
                  aria-label="Read this question aloud again"
                >
                  <Volume2 size={14} aria-hidden="true" />
                  Read aloud
                </button>
              </div>

              {/* Question text — receives focus so Tab starts here */}
              <p
                id="question-heading"
                ref={headingRef}
                tabIndex={-1}
                className="text-xl font-semibold text-white leading-relaxed mb-8 outline-none"
              >
                {currentQ.question}
              </p>

              {/* ── MCQ ── */}
              {currentQ.type === 'mcq' && (
                <fieldset
                  aria-labelledby="question-heading"
                  className="space-y-3"
                >
                  <legend className="sr-only">
                    Choose one answer for question {currentIdx + 1}
                  </legend>
                  {currentQ.options?.map((option, i) => {
                    const selected = answers[currentQ.id] === option
                    return (
                      <label
                        key={i}
                        className={[
                          'flex items-center gap-4 p-4 rounded-xl border-2 cursor-pointer transition-all',
                          selected
                            ? 'border-sky-500 bg-sky-950/60 text-sky-100'
                            : 'border-slate-700 hover:border-slate-500 text-slate-300 hover:text-white',
                        ].join(' ')}
                      >
                        <input
                          type="radio"
                          name={`question-${currentQ.id}`}
                          value={option}
                          checked={selected}
                          onChange={() => {
                            setAnswer(currentQ.id, option)
                            announce(`Selected: ${option}`)
                          }}
                          onFocus={() => speak(option)}
                          className={`w-5 h-5 accent-sky-500 flex-shrink-0 ${focusRing}`}
                        />
                        <span className="text-base font-medium">{option}</span>
                      </label>
                    )
                  })}
                </fieldset>
              )}

              {/* ── Short answer ── */}
              {currentQ.type === 'short_answer' && (
                <div className="space-y-5">
                  <div>
                    <label
                      htmlFor={`answer-${currentQ.id}`}
                      className="block text-sm font-semibold text-slate-400 mb-2"
                    >
                      Your answer
                      <span className="ml-2 text-xs text-slate-500 font-normal">
                        (type, or use the voice recorder below)
                      </span>
                    </label>
                    <textarea
                      id={`answer-${currentQ.id}`}
                      rows={5}
                      value={answers[currentQ.id] || ''}
                      onChange={(e) => setAnswer(currentQ.id, e.target.value)}
                      placeholder="Type your answer here, or use the voice recorder to answer verbally…"
                      aria-describedby={`voice-hint-${currentQ.id}`}
                      className={`w-full bg-slate-800 border border-slate-600 rounded-xl px-4 py-3 text-white placeholder:text-slate-500 text-sm leading-relaxed resize-none transition-all ${focusRing} focus:ring-sky-500 focus:border-sky-500`}
                    />
                    {/* sr-only hint referenced by aria-describedby */}
                    <p id={`voice-hint-${currentQ.id}`} className="sr-only">
                      You can answer verbally using the voice recorder below. Your speech
                      will be transcribed and appended to the text field above.
                    </p>
                  </div>

                  {/* Voice recorder */}
                  <div
                    className="border border-dashed border-slate-700 rounded-xl p-5"
                    role="region"
                    aria-label="Voice recording for this question"
                  >
                    <p className="text-xs text-slate-500 mb-3 font-medium flex items-center gap-1.5">
                      <Mic size={12} aria-hidden="true" />
                      Voice answer — transcription appends to the text box above
                    </p>
                    <AudioRecorder
                      onTranscription={(text) => {
                        const joined = ((answers[currentQ.id] || '') + ' ' + text).trimStart()
                        setAnswer(currentQ.id, joined)
                        announce(`Voice transcribed: ${text}`)
                      }}
                    />
                  </div>

                  {/* Read-back */}
                  {answers[currentQ.id]?.trim() && (
                    <button
                      onClick={() => speak('Your current answer is: ' + answers[currentQ.id])}
                      className={`text-xs text-slate-400 hover:text-sky-300 flex items-center gap-1.5 px-2 py-1 rounded-lg ${focusRing}`}
                      aria-label="Read my current answer aloud"
                    >
                      <Volume2 size={12} aria-hidden="true" />
                      Read my answer aloud
                    </button>
                  )}
                </div>
              )}
            </section>

            {/* Navigation row */}
            <nav aria-label="Question navigation" className="flex items-center justify-between gap-4">
              <button
                onClick={goPrev}
                disabled={currentIdx === 0}
                aria-label={
                  currentIdx === 0
                    ? 'No previous question'
                    : `Go to previous question, question ${currentIdx}`
                }
                className={`flex items-center gap-2 px-5 py-3 rounded-xl border border-slate-700 text-slate-300 font-semibold hover:border-slate-500 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-all ${focusRing}`}
              >
                <ChevronLeft size={18} aria-hidden="true" />
                Previous
              </button>

              <p className="text-slate-600 text-xs font-medium hidden sm:block" aria-hidden="true">
                ← → arrow keys also navigate
              </p>

              {currentIdx < questions.length - 1 ? (
                <button
                  onClick={goNext}
                  aria-label={`Go to next question, question ${currentIdx + 2} of ${questions.length}`}
                  className={`flex items-center gap-2 px-5 py-3 rounded-xl bg-sky-600 hover:bg-sky-500 text-white font-bold transition-all shadow-lg shadow-sky-900/40 ${focusRing}`}
                >
                  Next
                  <ChevronRight size={18} aria-hidden="true" />
                </button>
              ) : (
                <button
                  onClick={handleSubmit}
                  aria-label={`Submit assessment. ${answeredCount} of ${questions.length} questions answered.`}
                  className={`flex items-center gap-2 px-6 py-3 rounded-xl bg-green-600 hover:bg-green-500 text-white font-bold transition-all shadow-lg shadow-green-900/40 ${focusRing} focus:ring-green-400`}
                >
                  <CheckCircle size={18} aria-hidden="true" />
                  Submit Assessment
                </button>
              )}
            </nav>

            {/* Quick-jump pill strip — aids keyboard / Braille users jumping to any question */}
            <nav aria-label="Jump to any question" className="mt-10">
              <p className="text-xs text-slate-500 mb-3 font-medium">Jump to question:</p>
              <ol className="flex flex-wrap gap-2" role="list">
                {questions.map((q, i) => {
                  const done    = !!answers[q.id]?.trim()
                  const current = i === currentIdx
                  return (
                    <li key={q.id}>
                      <button
                        onClick={() => setCurrentIdx(i)}
                        aria-label={`Question ${i + 1}${done ? ', answered' : ', unanswered'}${current ? ', currently viewing' : ''}`}
                        aria-current={current ? 'step' : undefined}
                        className={[
                          'w-10 h-10 rounded-lg text-sm font-bold transition-all',
                          focusRing,
                          current
                            ? 'bg-sky-600 text-white'
                            : done
                              ? 'bg-green-900/60 text-green-300 border border-green-700'
                              : 'bg-slate-800 text-slate-400 border border-slate-700 hover:border-slate-500',
                        ].join(' ')}
                      >
                        {i + 1}
                      </button>
                    </li>
                  )
                })}
              </ol>
            </nav>
          </>
        )}

        {/* Submitting */}
        {phase === 'submitting' && (
          <div
            className="flex flex-col items-center justify-center min-h-[55vh] gap-5"
            role="status"
            aria-label="Submitting your assessment"
          >
            <Loader2 size={44} className="text-green-400 animate-spin" aria-hidden="true" />
            <p className="text-slate-300 text-xl font-semibold">Submitting your assessment…</p>
            <p className="text-slate-500 text-sm">
              Our AI evaluator is reviewing your answers. This takes a few seconds.
            </p>
          </div>
        )}

        {/* Done */}
        {phase === 'done' && result && (
          <div
            className="flex flex-col items-center text-center gap-8 min-h-[55vh] justify-center"
            role="region"
            aria-label="Assessment results"
          >
            <CheckCircle size={56} className="text-green-400" aria-hidden="true" />

            <div>
              <h2 className="text-3xl font-extrabold text-white mb-2">Assessment Complete</h2>
              <p className="text-slate-400 text-sm">
                Your results have been submitted to the hiring team.
              </p>
            </div>

            <div
              className="bg-slate-900 border border-slate-700 rounded-2xl p-8 max-w-md w-full"
              aria-labelledby="score-label"
            >
              <p id="score-label" className="text-sm font-semibold text-slate-400 mb-2">
                Technical Score
              </p>
              <p
                className="text-6xl font-extrabold text-sky-400 mb-4"
                aria-label={`${result.technical_score} out of 100`}
              >
                {result.technical_score}
                <span className="text-2xl text-slate-500 font-medium"> / 100</span>
              </p>
              <p className="text-slate-300 text-sm leading-relaxed">
                {result.reasoning_summary}
              </p>
            </div>

            <div className="flex gap-4">
              <button
                onClick={() => speak(
                  `Your score is ${result.technical_score} out of 100. ` +
                  result.reasoning_summary
                )}
                className={`flex items-center gap-2 px-5 py-3 rounded-xl border border-slate-700 text-slate-300 font-semibold hover:border-sky-600 hover:text-sky-300 transition-all ${focusRing}`}
                aria-label="Read result aloud"
              >
                <Volume2 size={16} aria-hidden="true" />
                Read result aloud
              </button>
              <button
                onClick={() => navigate('/dashboard')}
                className={`px-8 py-3 bg-sky-600 hover:bg-sky-500 text-white font-bold rounded-xl transition-all ${focusRing}`}
              >
                Return to Dashboard
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
