import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";

const api = async (path, options = {}) => {
  const response = await fetch(`/api${path}`, { headers: { "Content-Type": "application/json" }, ...options });
  if (!response.ok) throw await response.json();
  return response.status === 204 ? null : response.json();
};

function ConflictAlert({ error }) {
  if (!error?.error?.conflicts) return null;
  return <div className="alert"><strong>{error.error.message}</strong><ul>{error.error.conflicts.map((item, index) => <li key={index}>{item.date}: {item.detail}</li>)}</ul></div>;
}

function JobForm({ job, technicians, onClose, onSaved }) {
  const [form, setForm] = useState(job ? { ...job, start_time: job.start_time, recurrence_count: 1 } : { customer_name: "", description: "", technician_id: technicians[0]?.id || "", scheduled_date: new Date().toISOString().slice(0, 10), start_time: "09:00", duration_minutes: 60, status: "scheduled", recurrence_count: 1 });
  const [error, setError] = useState(null);
  const update = (key, value) => setForm({ ...form, [key]: value });
  const submit = async (event) => {
    event.preventDefault(); setError(null);
    try {
      const payload = { ...form, technician_id: Number(form.technician_id), duration_minutes: Number(form.duration_minutes), recurrence_count: Number(form.recurrence_count) };
      delete payload.id; delete payload.technician_name; delete payload.end_time; delete payload.series_id; delete payload.series_index; delete payload.series_total;
      if (job) delete payload.recurrence_count;
      const result = await api(job ? `/jobs/${job.id}` : "/jobs", { method: job ? "PATCH" : "POST", body: JSON.stringify(payload) });
      onSaved(result);
    } catch (e) { setError(e); }
  };
  return <div className="modal"><form onSubmit={submit}><h2>{job ? "Edit job" : "New job"}</h2><ConflictAlert error={error} />
    <label>Customer<input required value={form.customer_name} onChange={e => update("customer_name", e.target.value)} /></label>
    <label>Description<textarea required value={form.description} onChange={e => update("description", e.target.value)} /></label>
    <label>Technician<select required value={form.technician_id} onChange={e => update("technician_id", e.target.value)}>{technicians.map(t => <option key={t.id} value={t.id} disabled={!t.is_active}>{t.name}{t.is_active ? "" : " (Inactive)"}</option>)}</select></label>
    <label>Date<input type="date" required value={form.scheduled_date} onChange={e => update("scheduled_date", e.target.value)} /></label>
    <label>Start time<input type="time" required value={form.start_time} onChange={e => update("start_time", e.target.value)} /></label>
    <label>Duration<select value={form.duration_minutes} onChange={e => update("duration_minutes", e.target.value)}>{[30,60,90,120].map(d => <option key={d}>{d}</option>)}</select></label>
    {job ? <label>Status<select value={form.status} onChange={e => update("status", e.target.value)}><option value="scheduled">Scheduled</option><option value="in_progress">In Progress</option><option value="completed">Completed</option></select></label> : <label>Weekly occurrences<input type="number" min="1" max="12" value={form.recurrence_count} onChange={e => update("recurrence_count", e.target.value)} /></label>}
    <div><button type="submit">Save</button><button type="button" onClick={onClose}>Cancel</button></div>
  </form></div>;
}

function App() {
  const [jobs, setJobs] = useState([]); const [technicians, setTechnicians] = useState([]); const [editing, setEditing] = useState(null); const [filters, setFilters] = useState({});
  const load = () => api(`/jobs?${new URLSearchParams(Object.entries(filters).filter(([,v]) => v))}`).then(setJobs);
  useEffect(() => { api("/technicians").then(setTechnicians); }, []);
  useEffect(load, [filters]);
  const remove = async id => { if (confirm("Delete this job?")) { await api(`/jobs/${id}`, { method: "DELETE" }); load(); } };
  return <main><header><h1>TankTrack Scheduler</h1><button onClick={() => setEditing({})}>New job</button></header>
    <section className="filters"><input type="date" onChange={e => setFilters({ ...filters, date: e.target.value })} /><select onChange={e => setFilters({ ...filters, technician_id: e.target.value })}><option value="">All technicians</option>{technicians.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}</select><select onChange={e => setFilters({ ...filters, status: e.target.value })}><option value="">All statuses</option><option value="scheduled">Scheduled</option><option value="in_progress">In Progress</option><option value="completed">Completed</option></select></section>
    <table><thead><tr><th>Date</th><th>Time</th><th>Customer</th><th>Technician</th><th>Status</th><th /></tr></thead><tbody>{jobs.map(job => <tr key={job.id}><td>{job.scheduled_date}</td><td>{job.start_time}-{job.end_time}</td><td>{job.customer_name}{job.series_id && <small> Week {job.series_index} of {job.series_total}</small>}</td><td>{job.technician_name}</td><td>{job.status}</td><td><button onClick={() => setEditing(job)}>Edit</button><button onClick={() => remove(job.id)}>Delete</button></td></tr>)}</tbody></table>
    {editing && <JobForm job={editing.id ? editing : null} technicians={technicians} onClose={() => setEditing(null)} onSaved={() => { setEditing(null); load(); }} />}
  </main>;
}

createRoot(document.getElementById("root")).render(<App />);
