"use client";

import { useState } from "react";
import { UploadCloud, CheckCircle } from "lucide-react";

export default function UploadMedia({ onUploadComplete }: { onUploadComplete: (url: string) => void }) {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      setUploading(true);

      // Local mock implementation of S3 upload
      setTimeout(() => {
        setUploading(false);
        onUploadComplete(`https://s3.amazonaws.com/cstore-media/${selectedFile.name}`);
      }, 1500);
    }
  };

  return (
    <div className="flex items-center gap-4">
      <label className="cursor-pointer bg-gray-100 px-4 py-3 rounded-lg border border-gray-300 hover:bg-gray-200 flex items-center gap-2">
        <UploadCloud className="w-5 h-5 text-gray-600" />
        <span className="text-gray-700 font-medium">Capture Video/Photo</span>
        <input type="file" className="hidden" accept="image/*,video/*" onChange={handleFileChange} />
      </label>
      
      {uploading && <span className="text-blue-600 animate-pulse text-sm font-medium">Uploading to S3...</span>}
      {!uploading && file && <span className="text-green-600 flex items-center gap-1 text-sm font-bold"><CheckCircle className="w-4 h-4" /> Ready</span>}
    </div>
  );
}
