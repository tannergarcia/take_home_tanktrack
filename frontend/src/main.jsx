import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";

const api = async (path, options = {}) => {
  const response = await fetch(`/api${path}`, { headers: { "Content-Type": "application/json" }, ...options });
  if (!response.ok) throw await response.json();
  return response.status === 204 ? null : response.json();
};

function ErrorAlert({ error }) {
  const details = error?.error?.conflicts;
  if (!error) return null;
  return <div className="alert" role="alert">
    <strong>{error.error?.code === "validation_error" ? "Please check the form" : "Unable to save changes"}</strong>
    <p>{error.error?.message || "An unexpected error occurred. Please try again."}</p>
    {details && <ul>{details.map((item, index) => <li key={index}>{item.date}: {item.detail}</li>)}</ul>}
  </div>;
}

function SuccessAlert({ message, onDismiss }) {
  if (!message) return null;
  return <div className="success-alert" role="status">
    <span>{message}</span>
    <button type="button" aria-label="Dismiss success message" onClick={onDismiss}>×</button>
  </div>;
}

function statusLabel(status) {
  return {
    scheduled: "Scheduled",
    in_progress: "In Progress",
    completed: "Completed",
  }[status] || status;
}

function JobForm({ job, technicians, onClose, onSaved }) {
  const [form, setForm] = useState(job ? { ...job, start_time: job.start_time, recurrence_count: 1 } : { customer_name: "", description: "", technician_id: technicians[0]?.id || "", scheduled_date: new Date().toISOString().slice(0, 10), start_time: "09:00", duration_minutes: 60, status: "scheduled", recurrence_count: 1 });
  const [error, setError] = useState(null);
  const update = (key, value) => setForm({ ...form, [key]: value });
  const submit = async (event) => {
    event.preventDefault(); setError(null);
    try {
      const payload = { ...form, technician_id: Number(form.technician_id), duration_minutes: Number(form.duration_minutes), recurrence_count: Number(form.recurrence_count) };
      delete payload.id; delete payload.technician_name; delete payload.end_time; delete payload.deleted; delete payload.series_id; delete payload.series_index; delete payload.series_total;
      if (job) delete payload.recurrence_count;
      const result = await api(job ? `/jobs/${job.id}` : "/jobs", { method: job ? "PATCH" : "POST", body: JSON.stringify(payload) });
      onSaved(result);
    } catch (e) { setError(e); }
  };
  const editorClass = job ? "modal" : "side-panel";
  return <div className={editorClass} role={job ? "presentation" : "complementary"} aria-label={job ? undefined : "Create new job"}><form className="job-form" onSubmit={submit}><h2>{job ? "Edit job" : "New job"}</h2><ErrorAlert error={error} />
    <label>Customer<input required value={form.customer_name} onChange={e => update("customer_name", e.target.value)} /></label>
    <label>Description<textarea required value={form.description} onChange={e => update("description", e.target.value)} /></label>
    <label>Technician<select required value={form.technician_id} onChange={e => update("technician_id", e.target.value)}>{technicians.map(t => <option key={t.id} value={t.id} disabled={!t.is_active}>{t.name}{t.is_active ? "" : " (Inactive)"}</option>)}</select></label>
    <label>Date<input type="date" required value={form.scheduled_date} onChange={e => update("scheduled_date", e.target.value)} /></label>
    <label>Start time<input type="time" required value={form.start_time} onChange={e => update("start_time", e.target.value)} /></label>
    <label>Duration (minutes)<select value={form.duration_minutes} onChange={e => update("duration_minutes", e.target.value)}>{[30,60,90,120].map(d => <option key={d}>{d}</option>)}</select></label>
    <label>Status<select value={form.status} onChange={e => update("status", e.target.value)}><option value="scheduled">Scheduled</option><option value="in_progress">In Progress</option><option value="completed">Completed</option></select></label>
    {!job && <label>Repeat for x weeks<input type="number" min="1" max="12" value={form.recurrence_count} onChange={e => update("recurrence_count", e.target.value)} /></label>}
    <div><button type="submit">Save</button><button type="button" onClick={onClose}>Cancel</button></div>
  </form></div>;
}

function DeleteConfirmation({ job, onCancel, onConfirm, busy }) {
  return <div className="modal" role="presentation">
    <div className="confirm-dialog" role="alertdialog" aria-modal="true" aria-labelledby="delete-title">
      <h2 id="delete-title">Delete job?</h2>
      <p>This will remove the job for <strong>{job.customer_name}</strong> on {job.scheduled_date} from the schedule.</p>
      <div className="dialog-actions">
        <button type="button" onClick={onCancel} disabled={busy}>Keep job</button>
        <button type="button" className="danger" onClick={onConfirm} disabled={busy}>{busy ? "Deleting..." : "Delete job"}</button>
      </div>
    </div>
  </div>;
}

function App() {
  const [jobs, setJobs] = useState([]); const [technicians, setTechnicians] = useState([]); const [editing, setEditing] = useState(null); const [deleteTarget, setDeleteTarget] = useState(null); const [deleting, setDeleting] = useState(false); const [filters, setFilters] = useState({}); const [pageError, setPageError] = useState(null); const [successMessage, setSuccessMessage] = useState(null);
  const load = () => api(`/jobs?${new URLSearchParams(Object.entries(filters).filter(([,v]) => v))}`).then(results => { setJobs(results); setPageError(null); }).catch(setPageError);
  useEffect(() => { api("/technicians").then(setTechnicians).catch(setPageError); }, []);
  useEffect(() => { load(); }, [filters]);
  const remove = async () => {
    setDeleting(true);
    try {
      await api(`/jobs/${deleteTarget.id}`, { method: "DELETE" });
      setDeleteTarget(null);
      load();
    } catch (error) {
      setPageError(error);
    } finally {
      setDeleting(false);
    }
  };
  const handleSaved = () => {
    const wasModified = Boolean(editing?.id);
    setEditing(null);
    if (!wasModified) setSuccessMessage("Job created successfully.");
    load();
  };
  const createPanelOpen = editing && !editing.id;
  return <main className={createPanelOpen ? "panel-open" : ""}><header><h1>TankTrack Scheduler</h1><button onClick={() => { setSuccessMessage(null); setEditing({}); }}>New job</button></header>
    <ErrorAlert error={pageError} />
    <SuccessAlert message={successMessage} onDismiss={() => setSuccessMessage(null)} />
    <section className="filters"><input type="date" onChange={e => setFilters({ ...filters, date: e.target.value })} /><select onChange={e => setFilters({ ...filters, technician_id: e.target.value })}><option value="">Any technician</option>{technicians.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}</select><select onChange={e => setFilters({ ...filters, status: e.target.value })}><option value="">Any Status</option><option value="scheduled">Scheduled</option><option value="in_progress">In Progress</option><option value="completed">Completed</option></select></section>
    <table><thead><tr><th>Date</th><th>Time</th><th>Customer</th><th>Technician</th><th>Status</th><th /></tr></thead><tbody>{jobs.length ? jobs.map(job => <tr key={job.id}><td>{job.scheduled_date}</td><td>{job.start_time}-{job.end_time}</td><td>{job.customer_name}{job.series_id && <small> Week {job.series_index} of {job.series_total}</small>}</td><td>{job.technician_name}</td><td><span className={`status status-${job.status}`}>{statusLabel(job.status)}</span></td><td><button onClick={() => setEditing(job)}>Edit</button><button onClick={() => setDeleteTarget(job)}>Delete</button></td></tr>) : <tr><td className="empty" colSpan="6">No jobs match the selected filters.</td></tr>}</tbody></table>
    {editing && <JobForm job={editing.id ? editing : null} technicians={technicians} onClose={() => setEditing(null)} onSaved={handleSaved} />}
    {deleteTarget && <DeleteConfirmation job={deleteTarget} onCancel={() => setDeleteTarget(null)} onConfirm={remove} busy={deleting} />}
  </main>;
}

createRoot(document.getElementById("root")).render(<App />);
