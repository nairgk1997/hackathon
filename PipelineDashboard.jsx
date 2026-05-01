import { useState, useEffect } from 'react'
import {
  BarChart2, Users, Briefcase, CheckCircle2, Star,
  TrendingUp, AlertCircle, Loader2,
} from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell, Legend,
} from 'recharts'
import api from '../api/client'

// ── Palette (mirrors dashboard_service.py stage colors) ───────────────────────

const STAGE_COLORS = {
  Applied:      '#38bdf8',
  Shortlisted:  '#3b82f6',
  Assessed:     '#8b5cf6',
  Interviewing: '#f59e0b',
  Completed:    '#10b981',
  Rejected:     '#f87171',
}

// ── Summary card ──────────────────────────────────────────────────────────────

function StatCard({ label, value, icon: Icon, color }) {
  return (
    <div className="bg-white rounded-2xl border border-sky-200/80 shadow-lg shadow-sky-900/8 p-5 flex items-center gap-4">
      <div
        className="shrink-0 flex items-center justify-center w-12 h-12 rounded-xl"
        style={{ background: `${color}18` }}
      >
        <Icon size={22} style={{ color }} />
      </div>
      <div>
        <p className="text-2xl font-extrabold text-sky-950 leading-tight">{value ?? '—'}</p>
        <p className="text-xs text-sky-500 font-semibold mt-0.5">{label}</p>
      </div>
    </div>
  )
}

// ── Custom bar tooltip ────────────────────────────────────────────────────────

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-white border border-sky-200 rounded-xl shadow-lg px-4 py-3 text-xs">
      <p className="font-bold text-sky-900 mb-2">{label}</p>
      {payload.map((p) => (
        <div key={p.name} className="flex items-center gap-2 mt-1">
          <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ background: p.fill }} />
          <span className="text-sky-700">{p.name}:</span>
          <span className="font-bold text-sky-900">{p.value}</span>
        </div>
      ))}
    </div>
  )
}

// ── Score pill ────────────────────────────────────────────────────────────────

function ScorePill({ value }) {
  if (value == null) return <span className="text-sky-300 text-xs">—</span>
  const color =
    value >= 75 ? 'bg-emerald-100 text-emerald-700' :
    value >= 50 ? 'bg-amber-100 text-amber-700'     :
                  'bg-red-100 text-red-600'
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold ${color}`}>
      {value}%
    </span>
  )
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function PipelineDashboard() {
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState('')

  useEffect(() => {
    api.get('/pipeline/stats')
      .then((res) => setData(res.data))
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load pipeline data.'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen gap-4 text-sky-400">
        <Loader2 size={36} className="animate-spin" />
        <p className="text-sm font-medium">Loading pipeline data…</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center gap-3 m-8 bg-red-50 border border-red-200 text-red-600 text-sm px-5 py-4 rounded-2xl">
        <AlertCircle size={18} className="shrink-0" />
        {error}
      </div>
    )
  }

  const { summary, stage_distribution, jobs } = data

  // Build per-job bar chart data — one bar group per job
  const barData = jobs.map((j) => ({
    name: j.title.length > 22 ? `${j.title.slice(0, 20)}…` : j.title,
    Applied:      j.stages.applied,
    Shortlisted:  j.stages.shortlisted,
    Assessed:     j.stages.assessed,
    Interviewing: j.stages.interviewing,
    Completed:    j.stages.completed,
    Rejected:     j.stages.rejected,
  }))

  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-50/60 via-white to-blue-50/40 p-6 space-y-6">

      {/* ── Page header ── */}
      <div className="flex items-center gap-3">
        <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-sky-400 shadow-md shadow-sky-500/30">
          <BarChart2 size={20} className="text-white" />
        </div>
        <div>
          <h1 className="text-xl font-extrabold text-sky-950 leading-tight">Overall Pipeline View</h1>
          <p className="text-xs text-sky-500 font-medium mt-0.5">Live hiring funnel across all open roles</p>
        </div>
      </div>

      {/* ── Summary cards ── */}
      <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <StatCard label="Total Jobs"        value={summary.total_jobs}        icon={Briefcase}    color="#3b82f6" />
        <StatCard label="Total Candidates"  value={summary.total_candidates}  icon={Users}        color="#38bdf8" />
        <StatCard label="Shortlisted+"      value={summary.total_shortlisted} icon={Star}         color="#8b5cf6" />
        <StatCard label="Assessed+"         value={summary.total_assessed}    icon={TrendingUp}   color="#f59e0b" />
        <StatCard label="Interviewed+"      value={summary.total_interviewed} icon={CheckCircle2} color="#10b981" />
        <StatCard label="Completed"         value={summary.total_completed}   icon={CheckCircle2} color="#10b981" />
      </div>

      {/* ── Stage distribution bar chart ── */}
      <div className="bg-white rounded-2xl border border-sky-200/80 shadow-lg shadow-sky-900/8 p-6">
        <h2 className="text-sm font-bold text-sky-950 mb-5">Candidates by Stage &amp; Role</h2>

        {jobs.length === 0 ? (
          <p className="text-sm text-sky-400 text-center py-12">No jobs found.</p>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={barData} margin={{ top: 4, right: 16, left: -8, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
              <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#475569' }} axisLine={false} tickLine={false} />
              <YAxis allowDecimals={false} tick={{ fontSize: 10, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Legend
                iconType="circle"
                iconSize={8}
                formatter={(v) => <span style={{ fontSize: 11, color: '#475569' }}>{v}</span>}
              />
              {Object.entries(STAGE_COLORS).map(([stage, color]) => (
                <Bar key={stage} dataKey={stage} stackId="a" fill={color} radius={stage === 'Rejected' ? [4, 4, 0, 0] : [0, 0, 0, 0]} />
              ))}
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* ── Per-job table ── */}
      <div className="bg-white rounded-2xl border border-sky-200/80 shadow-lg shadow-sky-900/8 overflow-hidden">
        <div className="px-6 py-4 border-b border-sky-100">
          <h2 className="text-sm font-bold text-sky-950">Per-Role Breakdown</h2>
        </div>

        {jobs.length === 0 ? (
          <p className="text-sm text-sky-400 text-center py-12">No data yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-sky-50 text-xs font-semibold text-sky-600 uppercase tracking-wide">
                  <th className="px-5 py-3 text-left">Role</th>
                  <th className="px-4 py-3 text-left">Level</th>
                  <th className="px-4 py-3 text-center">Total</th>
                  {Object.keys(STAGE_COLORS).map((s) => (
                    <th key={s} className="px-3 py-3 text-center">{s}</th>
                  ))}
                  <th className="px-4 py-3 text-center">Avg Match</th>
                  <th className="px-4 py-3 text-center">Avg Tech</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-sky-50">
                {jobs.map((job) => (
                  <tr key={job.job_id} className="hover:bg-sky-50/50 transition-colors">
                    <td className="px-5 py-3 font-semibold text-sky-900 max-w-[180px] truncate">{job.title}</td>
                    <td className="px-4 py-3 text-sky-600 text-xs">{job.experience_level}</td>
                    <td className="px-4 py-3 text-center font-bold text-sky-900">{job.total_candidates}</td>
                    {Object.keys(STAGE_COLORS).map((s) => {
                      const key = s.toLowerCase()
                      const count = job.stages[key] ?? 0
                      return (
                        <td key={s} className="px-3 py-3 text-center">
                          {count > 0 ? (
                            <span
                              className="inline-flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold text-white"
                              style={{ background: STAGE_COLORS[s] }}
                            >
                              {count}
                            </span>
                          ) : (
                            <span className="text-sky-200 text-xs">—</span>
                          )}
                        </td>
                      )
                    })}
                    <td className="px-4 py-3 text-center"><ScorePill value={job.avg_match_score} /></td>
                    <td className="px-4 py-3 text-center"><ScorePill value={job.avg_tech_score} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
