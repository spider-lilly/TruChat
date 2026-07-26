import { useState } from "react";

const UploadModal = ({ isOpen, onClose, onAttach }) => {
  const [url, setUrl] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);

  if (!isOpen) return null;

  const handleAddLink = () => {
    if (url.trim()) {
      onAttach({ type: "link", value: url.trim() });
      setUrl("");
      onClose();
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file.name);
      onAttach({ type: "image", value: file.name, file });
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-xs font-serif">
      <div className="bg-[#FAF8F5] border-2 border-neutral-900 p-6 w-full max-w-md shadow-2xl relative">
        <button
          onClick={onClose}
          className="absolute top-3 right-3 text-neutral-600 hover:text-black font-bold text-sm"
        >
          ✕
        </button>

        <h3 className="text-xs uppercase tracking-widest font-extrabold text-neutral-900 border-b border-neutral-400 pb-2 mb-5">
          ATTACH ARTICLE IMAGE OR LINK
        </h3>

        <div className="space-y-5">
          {/* Image Upload Area */}
          <div className="border-2 border-dashed border-neutral-400 p-6 text-center bg-[#F7F4ED] hover:border-neutral-700 transition-colors">
            <label className="cursor-pointer block space-y-2">
              <div className="w-10 h-10 mx-auto border border-neutral-700 flex items-center justify-center text-lg font-bold">
                📷
              </div>
              <div className="text-xs uppercase tracking-wider font-bold text-neutral-900 border border-neutral-900 py-1.5 px-4 inline-block bg-white hover:bg-neutral-100">
                {selectedFile ? selectedFile : "UPLOAD ARTICLE IMAGE"}
              </div>
              <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="hidden"
              />
            </label>
          </div>

          <div className="text-center text-xs uppercase tracking-widest text-neutral-400 font-sans">
            — OR —
          </div>

          {/* Link URL Input */}
          <div className="flex gap-2">
            <input
              type="url"
              placeholder="https://example.com/article"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="flex-1 border border-neutral-400 bg-white px-3 py-2 text-xs font-mono focus:outline-none focus:border-neutral-900"
            />
            <button
              onClick={handleAddLink}
              className="bg-neutral-900 text-white text-xs font-bold px-4 py-2 uppercase tracking-wider hover:bg-neutral-800"
            >
              ADD
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadModal;
