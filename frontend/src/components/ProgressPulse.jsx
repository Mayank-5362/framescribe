export default function ProgressPulse({ label }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-4">
      <p className="text-xs text-slate-300">{label}</p>
      <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-white/5">
        <div className="h-full w-2/3 animate-pulse rounded-full bg-gradient-to-r from-sky-300 to-orange-300" />
      </div>
    </div>
  );
}
