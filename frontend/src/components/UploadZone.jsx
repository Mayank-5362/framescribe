import { useState } from "react";

const ACCEPTED_EXTENSIONS = ".mp4,.mov,.mkv,.webm,.avi";

export default function UploadZone({ onFileSelected, disabled, file }) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDrop = (event) => {
    event.preventDefault();
    if (disabled) return;

    setIsDragging(false);
    const dropped = event.dataTransfer.files?.[0];
    if (dropped) {
      onFileSelected(dropped);
    }
  };

  const handlePick = (event) => {
    const picked = event.target.files?.[0];
    if (picked) {
      onFileSelected(picked);
    }
  };

  return (
    <label
      className={`mt-5 block cursor-pointer rounded-2xl border border-dashed px-4 py-8 text-center transition ${
        isDragging ? "border-sky-300 bg-sky-400/10" : "border-white/10"
      } ${disabled ? "opacity-50 pointer-events-none" : "hover:border-sky-300"}`}
      onDragOver={(event) => {
        event.preventDefault();
        if (!disabled) setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
    >
      <input
        type="file"
        accept={ACCEPTED_EXTENSIONS}
        className="hidden"
        onChange={handlePick}
        disabled={disabled}
      />
      <div className="space-y-2">
        <p className="text-sm text-slate-300">Drag & drop a video file</p>
        <p className="text-xs text-slate-500">MP4, MOV, MKV, WEBM, AVI</p>
        {file && (
          <p className="text-xs text-slate-200">
            Selected: {file.name} ({Math.round(file.size / (1024 * 1024))} MB)
          </p>
        )}
      </div>
    </label>
  );
}
