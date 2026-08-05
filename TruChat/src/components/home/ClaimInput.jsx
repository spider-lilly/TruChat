import { useState } from "react";
import UploadModal from "./UploadModal";

const ClaimInput = ({ onSubmitClaim, isSubmitting }) => {
  const [claimText, setClaimText] = useState("");
  const [attachments, setAttachments] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const hasContent = claimText.trim().length > 0 || attachments.length > 0;

  const handleSubmit = () => {
    if (!hasContent || isSubmitting) return;
    onSubmitClaim(claimText.trim(), attachments);
  };

  const handleAttach = (attachment) => {
    setAttachments((prev) => [...prev, attachment]);
  };

  const removeAttachment = (index) => {
    setAttachments((prev) => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="border border-neutral-400 bg-white p-5 space-y-4 font-serif shadow-xs">
      <div className="flex justify-between items-center border-b border-neutral-300 pb-2">
        <h3 className="text-xs uppercase tracking-widest font-extrabold text-neutral-900">
          ENTER CLAIM FOR VERIFICATION
        </h3>
        {attachments.length > 0 && (
          <span className="text-[11px] text-neutral-500 font-sans">
            {attachments.length} attachment(s)
          </span>
        )}
      </div>

      {/* Attachments preview */}
      {attachments.length > 0 && (
        <div className="flex flex-wrap gap-2 pt-1">
          {attachments.map((att, idx) => (
            <span
              key={idx}
              className="inline-flex items-center gap-1.5 text-xs bg-[#F7F4ED] border border-neutral-400 px-2.5 py-1 text-neutral-800"
            >
              <span>{att.type === "image" ? "📷" : "🔗"}</span>
              <span className="truncate max-w-[200px]">{att.value}</span>
              <button
                onClick={() => removeAttachment(idx)}
                className="text-neutral-500 hover:text-black font-bold ml-1"
              >
                ✕
              </button>
            </span>
          ))}
        </div>
      )}

      {/* Input Textarea */}
      <textarea
        rows={4}
        value={claimText}
        onChange={(e) => setClaimText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type or paste any news claim, statement, or headline here..."
        className="w-full resize-none text-sm text-neutral-900 placeholder-neutral-400 focus:outline-none font-serif leading-relaxed"
      />

      {/* Controls Strip */}
      <div className="flex flex-wrap items-center justify-between border-t border-neutral-300 pt-3 gap-3">
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => setIsModalOpen(true)}
            className="w-8 h-8 border border-neutral-400 flex items-center justify-center font-bold text-lg text-neutral-800 hover:bg-neutral-100 hover:border-black transition-colors"
            title="Attach image or link"
          >
            +
          </button>
          <span className="text-[10px] uppercase tracking-wider text-neutral-500 font-mono hidden sm:inline">
            ENTER TO SUBMIT · SHIFT+ENTER FOR NEW LINE
          </span>
        </div>

        <button
          type="button"
          onClick={handleSubmit}
          disabled={!hasContent || isSubmitting}
          className={`px-5 py-2 text-xs font-bold uppercase tracking-wider transition-all flex items-center gap-2 ${
            !hasContent || isSubmitting
              ? "bg-neutral-300 text-neutral-500 cursor-not-allowed"
              : "bg-neutral-900 text-white hover:bg-neutral-800 active:scale-98"
          }`}
        >
          {isSubmitting ? "Verifying Claim..." : "Verify Claim →"}
        </button>
      </div>

      {/* Upload Modal */}
      <UploadModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onAttach={handleAttach}
      />
    </div>
  );
};

export default ClaimInput;
