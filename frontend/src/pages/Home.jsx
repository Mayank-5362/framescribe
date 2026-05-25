import { useEffect, useState } from "react";
import UploadZone from "../components/UploadZone.jsx";
import StatusBadge from "../components/StatusBadge.jsx";
import ProgressPulse from "../components/ProgressPulse.jsx";
import VideoPreview from "../components/VideoPreview.jsx";
import {
  createUploadUrl,
  getProgress,
  startProcessing,
  uploadToSignedUrl,
  uploadVideo,
} from "../services/api.js";
import frameScribeLogo from "../assets/framescribe-logo.png";

const STATUS_LABELS = {
  idle: "Idle",
  queued: "Queued",
  processing: "Processing",
  done: "Completed",
  error: "Error",
};

const STAGE_LABELS = {
  queued: "Waiting in queue",
  uploading_input: "Uploading video",
  downloading_input: "Downloading upload",
  extracting_audio: "Extracting audio",
  transcribing: "Transcribing with whisper.cpp",
  writing_subtitles: "Writing subtitles",
  uploading_outputs: "Uploading outputs",
  burning_subtitles: "Burning subtitles into video",
  done: "Completed",
};

const THEME_OPTIONS = [
  { value: "aurora", label: "Aurora" },
  { value: "sahara", label: "Sahara" },
  { value: "neon", label: "Neon" },
  { value: "graphite", label: "Graphite" },
  { value: "mint", label: "Mint" },
];

const FEATURE_ITEMS = [
  "Low RAM friendly",
  "Whisper.cpp transcription",
  "FFmpeg subtitle burn-in",
  "Queue-based processing",
  "Download SRT + VTT",
  "No sign-up required",
];

export default function Home({ theme, setTheme }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [jobId, setJobId] = useState(null);
  const [stage, setStage] = useState("queued");
  const [detail, setDetail] = useState("");

  const isBusy = status === "processing" || status === "queued";
  const progressLabel = detail || STAGE_LABELS[stage] || "Working";

  const handleFileSelected = (file) => {
    setSelectedFile(file);
    setStatus("idle");
    setError("");
    setResult(null);
    setJobId(null);
    setStage("queued");
    setDetail("");
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError("Please select a video file first.");
      setStatus("error");
      return;
    }

    setStatus("processing");
    setStage("uploading_input");
    setDetail("Uploading to storage");
    setError("");

    try {
      const init = await createUploadUrl(selectedFile.name);
      await uploadToSignedUrl(init.upload_url, selectedFile);
      const data = await startProcessing(init.job_id, init.storage_path);
      setJobId(data.job_id);
      setStatus(data.status || "queued");
      setStage(data.stage || "queued");
      setDetail("");
    } catch (err) {
      try {
        const data = await uploadVideo(selectedFile);
        setJobId(data.job_id);
        setStatus(data.status || "queued");
        setStage("queued");
        setDetail("");
      } catch (fallbackError) {
        setStatus("error");
        setError(
          err.message || fallbackError.message || "Upload failed. Please try again."
        );
      }
    }
  };

  useEffect(() => {
    if (!jobId) return undefined;

    let cancelled = false;

    const poll = async () => {
      try {
        const data = await getProgress(jobId);
        if (cancelled) return;

        setStatus(data.status || "processing");
        setStage(data.stage || "processing");
        setDetail(data.detail || "");

        if (data.status === "done") {
          setResult(data);
          return;
        }

        if (data.status === "error") {
          setError(data.detail || "Processing failed. Please try again.");
          return;
        }

        setTimeout(poll, 2000);
      } catch (err) {
        if (cancelled) return;
        setStatus("error");
        setError(err.message || "Unable to fetch progress.");
      }
    };

    poll();

    return () => {
      cancelled = true;
    };
  }, [jobId]);

  return (
    <div className="px-4 py-10 md:py-16">
      <div className="mx-auto max-w-6xl">
        <header className="flex flex-col gap-5 md:flex-row md:items-center md:justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center overflow-hidden rounded-2xl border border-white/10 bg-white/5">
              <img
                src={frameScribeLogo}
                alt="FrameScribe logo"
                className="h-full w-full object-cover object-left"
              />
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-slate-400">
                Whisper + FFmpeg
              </p>
              <p className="text-lg font-semibold">FrameScribe</p>
            </div>
          </div>
          <nav className="flex flex-wrap items-center gap-4">
            <a className="link-accent" href="#how-it-works">How it works</a>
            <a className="link-accent" href="#features">Features</a>
            <a className="link-accent" href="#security">Security</a>
            <a className="link-accent" href="#contact">Contact</a>
          </nav>
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs uppercase tracking-[0.3em] text-slate-400">
              Theme
            </span>
            {THEME_OPTIONS.map((option) => (
              <button
                key={option.value}
                type="button"
                className={`theme-pill ${theme === option.value ? "is-active" : ""}`}
                onClick={() => setTheme(option.value)}
                aria-pressed={theme === option.value}
              >
                {option.label}
              </button>
            ))}
          </div>
        </header>

        <section className="mt-10 text-center">
          <h1 className="text-4xl md:text-5xl font-semibold accent-text">
            FrameScribe
          </h1>
          <p className="mt-4 text-slate-300 max-w-2xl mx-auto">
            FrameScribe lets you upload a video, generate English subtitles, and
            burn them into the final video in one simple flow.
          </p>
          <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
            <span className="chip-accent">100% free to use</span>
            <span className="chip-muted">No account required</span>
            <span className="chip-muted">Whisper.cpp + FFmpeg</span>
          </div>
        </section>

        <section className="mt-10 grid gap-6 md:grid-cols-[1.1fr_0.9fr]">
          <div className="glass-card rounded-3xl p-6 md:p-8 soft-ring">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">Upload Video</h2>
              <StatusBadge status={status} label={STATUS_LABELS[status]} />
            </div>

            <UploadZone
              onFileSelected={handleFileSelected}
              disabled={isBusy}
              file={selectedFile}
            />

            <button
              className="btn-primary mt-6 w-full disabled:opacity-60 disabled:cursor-not-allowed"
              onClick={handleUpload}
              disabled={isBusy}
            >
              {isBusy
                ? "Processing..."
                : "Generate Subtitles"}
            </button>

            {(status === "processing" || status === "queued") && (
              <div className="mt-6">
                <ProgressPulse label={`Step: ${progressLabel}`} />
              </div>
            )}

            {error && (
              <div className="mt-6 rounded-2xl border border-red-400/30 bg-red-500/10 px-4 py-3 text-sm text-red-200">
                {error}
              </div>
            )}
          </div>

          <div className="glass-card rounded-3xl p-6 md:p-8">
            <h2 className="text-lg font-semibold">Output Preview</h2>
            <p className="mt-2 text-sm text-slate-400">
              The processed video appears here once the subtitles are ready.
            </p>

            <div className="mt-6">
              {result ? (
                <VideoPreview
                  outputFilename={result.output_filename}
                  subtitleFilename={result.srt_filename}
                  vttFilename={result.vtt_filename}
                  outputUrl={result.output_url}
                  subtitleUrl={result.srt_url}
                  vttUrl={result.vtt_url}
                />
              ) : (
                <div className="rounded-2xl border border-dashed border-white/15 p-6 text-center text-sm text-slate-500">
                  No output yet. Upload a video to get started.
                </div>
              )}
            </div>
          </div>
        </section>

        <section id="features" className="mt-10 grid gap-4 md:grid-cols-3">
          {FEATURE_ITEMS.map((item) => (
            <div
              key={item}
              className="glass-card rounded-2xl px-4 py-4 text-center text-sm text-slate-300"
            >
              {item}
            </div>
          ))}
        </section>

        <section id="how-it-works" className="mt-12 grid gap-6 md:grid-cols-2">
          <div className="glass-card rounded-3xl p-6 md:p-8">
            <h3 className="text-lg font-semibold">How it works</h3>
            <ol className="mt-4 space-y-3 text-sm text-slate-300">
              {[
                "Upload any supported video format.",
                "FFmpeg extracts audio to a clean WAV file.",
                "whisper.cpp transcribes English captions.",
                "SRT/VTT captions are generated.",
                "FFmpeg burns subtitles into the final video.",
              ].map((step, index) => (
                <li key={step} className="flex gap-3">
                  <span className="mt-0.5 h-6 w-6 rounded-full border border-sky-300/40 bg-sky-400/10 text-center text-xs leading-6 text-sky-200">
                    {index + 1}
                  </span>
                  <span>{step}</span>
                </li>
              ))}
            </ol>
          </div>

          <div className="glass-card rounded-3xl p-6 md:p-8">
            <h3 className="text-lg font-semibold">Free and simple</h3>
            <p className="mt-3 text-sm text-slate-300">
              This project is completely free to use. There are no subscriptions,
              credits, or hidden fees. Run it locally or deploy it on your own
              server for full control.
            </p>
            <div className="mt-4 grid gap-3 text-sm text-slate-300">
              <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                Progress updates with clear stages.
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                Download the final video and SRT subtitles.
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                Optimized for low-end laptops and small files.
              </div>
            </div>
          </div>
        </section>

        <section className="mt-6 grid gap-6 md:grid-cols-2">
          <div id="security" className="glass-card rounded-3xl p-6 md:p-8">
            <h3 className="text-lg font-semibold">Security & privacy</h3>
            <ul className="mt-4 space-y-3 text-sm text-slate-300">
              <li>Files are processed only on the server running this app.</li>
              <li>No accounts, tracking, or third-party uploads built in.</li>
              <li>Outputs are stored in the local outputs folder until removed.</li>
            </ul>
          </div>
          <div id="contact" className="glass-card rounded-3xl p-6 md:p-8">
            <h3 className="text-lg font-semibold">Contact</h3>
            <p className="mt-3 text-sm text-slate-300">
              Need help or want features? Reach out and we will reply quickly.
            </p>
            <div className="mt-4 flex flex-wrap gap-3">
              <a
                href="mailto:support@yourdomain.com"
                className="btn-primary"
              >
                Email support
              </a>
              <a
                href="https://github.com/your-org/your-repo"
                className="btn-secondary"
                target="_blank"
                rel="noreferrer"
              >
                Project repo
              </a>
            </div>
            <p className="mt-3 text-xs text-slate-500">
              Replace the contact links with your real email and repo URL.
            </p>
          </div>
        </section>

        <footer className="mt-12 border-t border-white/10 py-8 text-sm text-slate-400">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <p>
              Built for creators. Free to use, open-source friendly, and ready to
              run anywhere.
            </p>
            <div className="flex flex-wrap gap-4">
              <a className="link-accent" href="#how-it-works">How it works</a>
              <a className="link-accent" href="#security">Security</a>
              <a className="link-accent" href="#contact">Contact</a>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
