const styles = {
  idle: "bg-white/10 text-slate-300",
  queued: "bg-indigo-400/20 text-indigo-200",
  processing: "bg-sky-400/20 text-sky-200",
  done: "bg-emerald-400/20 text-emerald-200",
  error: "bg-red-400/20 text-red-200",
};

export default function StatusBadge({ status, label }) {
  return (
    <span
      className={`rounded-full px-3 py-1 text-xs font-semibold ${
        styles[status] || styles.idle
      }`}
    >
      {label}
    </span>
  );
}
