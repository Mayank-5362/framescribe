import { API_BASE_URL } from "../services/api.js";

export default function VideoPreview({
  outputFilename,
  subtitleFilename,
  vttFilename,
  outputUrl,
  subtitleUrl,
  vttUrl,
}) {
  const videoUrl =
    outputUrl || `${API_BASE_URL}/download/${outputFilename}`;
  const srtUrl =
    subtitleUrl || `${API_BASE_URL}/download/${subtitleFilename}`;
  const captionVttUrl = vttUrl
    ? vttUrl
    : vttFilename
    ? `${API_BASE_URL}/download/${vttFilename}`
    : null;

  return (
    <div className="space-y-4">
      <div className="overflow-hidden rounded-2xl border border-white/10">
        <video className="w-full" controls src={videoUrl} />
      </div>
      <div className="flex flex-wrap gap-3">
        <a
          href={videoUrl}
          className="rounded-full bg-sky-400/90 px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-sky-300"
          download
        >
          Download Video
        </a>
        <a
          href={srtUrl}
          className="rounded-full border border-white/15 px-4 py-2 text-sm text-slate-200 transition hover:border-sky-300"
          download
        >
          Download SRT
        </a>
        {captionVttUrl && (
          <a
            href={captionVttUrl}
            className="rounded-full border border-white/15 px-4 py-2 text-sm text-slate-200 transition hover:border-sky-300"
            download
          >
            Download VTT
          </a>
        )}
      </div>
    </div>
  );
}
