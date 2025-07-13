import { ChangeEvent } from 'react';

type ImageUploaderProps = {
  image: File | null;
  onUpload: (file: File) => void;
  onAnalyze: () => void;
  isLoading: boolean;
};

const ImageUploader = ({ image, onUpload, onAnalyze, isLoading }: ImageUploaderProps) => {
  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onUpload(e.target.files[0]);
    }
  };

  return (
    <div className="image-uploader">
      <h3>上传LeetCode截图</h3>
      <input 
        type="file" 
        accept="image/*" 
        onChange={handleFileChange}
        disabled={isLoading}
      />
      {image && (
        <div className="preview-section">
          <p>已选择文件: {image.name}</p>
          <button 
            onClick={onAnalyze}
            disabled={isLoading}
          >
            {isLoading ? '解析中...' : '开始解析'}
          </button>
        </div>
      )}
      <div className="instructions">
        <p>请确保截图包含:</p>
        <ul>
          <li>LeetCode个人主页</li>
          <li>已解决的题目列表</li>
          <li>题目难度标识</li>
        </ul>
      </div>
    </div>
  );
};

export default ImageUploader;
