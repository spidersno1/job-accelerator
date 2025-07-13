import { ChangeEvent, useState } from 'react';

type UploadMode = 'file' | 'text' | 'image';

type CodeUploaderProps = {
  onUpload: (data: { type: UploadMode; content: string | File; filename?: string }) => void;
  onAnalyze: () => void;
  isLoading: boolean;
  uploadedData: { type: UploadMode; content: string | File; filename?: string } | null;
};

const CodeUploader = ({ onUpload, onAnalyze, isLoading, uploadedData }: CodeUploaderProps) => {
  const [mode, setMode] = useState<UploadMode>('file');
  const [textContent, setTextContent] = useState('');

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      onUpload({ 
        type: mode, 
        content: file, 
        filename: file.name 
      });
    }
  };

  const handleTextSubmit = () => {
    if (textContent.trim()) {
      onUpload({ 
        type: 'text', 
        content: textContent.trim() 
      });
    }
  };

  const getFileAccept = () => {
    switch (mode) {
      case 'image':
        return 'image/*';
      case 'file':
        return '.js,.jsx,.ts,.tsx,.py,.java,.cpp,.c,.cs,.go,.php,.rb,.swift,.kt,.scala,.rs,.dart,.vue,.html,.css,.sql,.json,.xml,.yaml,.yml,.md,.txt';
      default:
        return '*';
    }
  };

  const getInstructions = () => {
    switch (mode) {
      case 'image':
        return {
          title: '上传代码截图',
          items: [
            'GitHub代码页面截图',
            'LeetCode解题记录',
            '项目代码片段',
            '技能证书或认证'
          ]
        };
      case 'file':
        return {
          title: '上传代码文件',
          items: [
            '支持常见编程语言文件',
            '项目配置文件 (package.json, requirements.txt)',
            '文档文件 (README.md, 技术文档)',
            '数据文件 (JSON, YAML, CSV)'
          ]
        };
      case 'text':
        return {
          title: '直接输入代码',
          items: [
            '粘贴代码片段',
            '项目描述',
            '技能列表',
            '学习经历'
          ]
        };
      default:
        return { title: '', items: [] };
    }
  };

  const instructions = getInstructions();

  return (
    <div className="code-uploader bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-xl font-semibold mb-4">上传代码进行技能分析</h3>
      
      {/* 模式选择 */}
      <div className="mode-selector mb-6">
        <div className="flex space-x-4">
          <button
            onClick={() => setMode('file')}
            className={`px-4 py-2 rounded-md transition-colors ${
              mode === 'file' 
                ? 'bg-blue-500 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            📁 文件上传
          </button>
          <button
            onClick={() => setMode('text')}
            className={`px-4 py-2 rounded-md transition-colors ${
              mode === 'text' 
                ? 'bg-blue-500 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            📝 文本输入
          </button>
          <button
            onClick={() => setMode('image')}
            className={`px-4 py-2 rounded-md transition-colors ${
              mode === 'image' 
                ? 'bg-blue-500 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            🖼️ 图片上传
          </button>
        </div>
      </div>

      {/* 上传区域 */}
      <div className="upload-area mb-6">
        {mode === 'text' ? (
          <div className="text-input-area">
            <textarea
              value={textContent}
              onChange={(e) => setTextContent(e.target.value)}
              placeholder="请输入代码、项目描述、技能列表等内容..."
              className="w-full h-40 p-4 border border-gray-300 rounded-md resize-y focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
            <button
              onClick={handleTextSubmit}
              disabled={isLoading || !textContent.trim()}
              className="mt-3 px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {isLoading ? '处理中...' : '提交文本'}
            </button>
          </div>
        ) : (
          <div className="file-input-area">
            <input
              type="file"
              accept={getFileAccept()}
              onChange={handleFileChange}
              disabled={isLoading}
              className="w-full p-3 border border-gray-300 rounded-md file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
          </div>
        )}
      </div>

      {/* 已上传内容预览 */}
      {uploadedData && (
        <div className="preview-section mb-6 p-4 bg-gray-50 rounded-md">
          <h4 className="font-semibold mb-2">已上传内容:</h4>
          {uploadedData.type === 'text' ? (
            <div className="text-preview">
              <p className="text-sm text-gray-600">文本内容 ({(uploadedData.content as string).length} 字符)</p>
              <div className="mt-2 p-3 bg-white rounded border text-sm max-h-32 overflow-y-auto">
                {(uploadedData.content as string).substring(0, 200)}
                {(uploadedData.content as string).length > 200 && '...'}
              </div>
            </div>
          ) : (
            <div className="file-preview">
              <p className="text-sm text-gray-600">
                文件: {uploadedData.filename} 
                {uploadedData.type === 'image' && ' (图片)'}
              </p>
            </div>
          )}
          
          <button
            onClick={onAnalyze}
            disabled={isLoading}
            className="mt-3 px-6 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {isLoading ? '分析中...' : '开始分析'}
          </button>
        </div>
      )}

      {/* 使用说明 */}
      <div className="instructions bg-blue-50 p-4 rounded-md">
        <h4 className="font-semibold text-blue-800 mb-2">{instructions.title}</h4>
        <ul className="text-sm text-blue-700 space-y-1">
          {instructions.items.map((item, index) => (
            <li key={index}>• {item}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default CodeUploader; 