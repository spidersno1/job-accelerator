import { useState } from 'react';
import { LeetCodeData } from './LeetCodeAnalysis';

interface OCRResultEditorProps {
  data: LeetCodeData;
  onSubmit: (data: LeetCodeData | null) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

const OCRResultEditor = ({ data, onSubmit, onCancel, isLoading = false }: OCRResultEditorProps) => {
  const [editedData, setEditedData] = useState<LeetCodeData>(data);

  const handleNumberChange = (field: 'easy' | 'medium' | 'hard') => 
    (e: React.ChangeEvent<HTMLInputElement>) => {
      setEditedData({
        ...editedData,
        stats: {
          ...editedData.stats,
          [field]: parseInt(e.target.value) || 0
        }
      });
    };

  const handleLanguageToggle = (lang: string) => {
    setEditedData({
      ...editedData,
      languages: editedData.languages.includes(lang)
        ? editedData.languages.filter((l: string) => l !== lang)
        : [...editedData.languages, lang]
    });
  };

  return (
    <div className="ocr-result-editor">
      <h3>编辑解析结果</h3>
      
      <div className="input-section">
        <label>
          简单题数量:
          <input 
            type="number" 
            value={editedData.stats.easy}
            onChange={handleNumberChange('easy')}
            min="0"
          />
        </label>
        <label>
          中等题数量:
          <input 
            type="number" 
            value={editedData.stats.medium}
            onChange={handleNumberChange('medium')}
            min="0"
          />
        </label>
        <label>
          难题数量:
          <input 
            type="number" 
            value={editedData.stats.hard}
            onChange={handleNumberChange('hard')}
            min="0"
          />
        </label>
      </div>

      <div className="languages-section">
        <h4>使用语言</h4>
        <div className="language-tags">
          {['Python', 'Java', 'C++', 'JavaScript', 'Go'].map(lang => (
            <button
              key={lang}
              className={editedData.languages.includes(lang) ? 'active' : ''}
              onClick={() => handleLanguageToggle(lang)}
              type="button"
            >
              {lang}
            </button>
          ))}
        </div>
      </div>

      <div className="button-group">
        <button 
          onClick={() => onSubmit(editedData)}
          disabled={isLoading}
        >
          {isLoading ? '保存中...' : '保存'}
        </button>
        <button 
          onClick={onCancel}
          disabled={isLoading}
        >
          取消
        </button>
      </div>
    </div>
  );
};

export default OCRResultEditor;
