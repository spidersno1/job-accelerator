import { useState } from 'react';

type ManualInputProps = {
  onSubmit: (data: {
    easy: number;
    medium: number;
    hard: number;
    languages: string[];
  }) => void;
};

const ManualInput = ({ onSubmit }: ManualInputProps) => {
  const [formData, setFormData] = useState({
    easy: 0,
    medium: 0,
    hard: 0,
    languages: [] as string[]
  });

  const handleNumberChange = (field: 'easy' | 'medium' | 'hard') => 
    (e: React.ChangeEvent<HTMLInputElement>) => {
      setFormData({
        ...formData,
        [field]: parseInt(e.target.value) || 0
      });
    };

  const handleLanguageToggle = (lang: string) => {
    setFormData({
      ...formData,
      languages: formData.languages.includes(lang)
        ? formData.languages.filter(l => l !== lang)
        : [...formData.languages, lang]
    });
  };

  const handleSubmit = () => {
    onSubmit(formData);
  };

  return (
    <div className="manual-input">
      <h3>手动输入LeetCode数据</h3>
      
      <div className="input-section">
        <label>
          简单题数量:
          <input 
            type="number" 
            value={formData.easy}
            onChange={handleNumberChange('easy')}
            min="0"
          />
        </label>
        <label>
          中等题数量:
          <input 
            type="number" 
            value={formData.medium}
            onChange={handleNumberChange('medium')}
            min="0"
          />
        </label>
        <label>
          难题数量:
          <input 
            type="number" 
            value={formData.hard}
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
              className={formData.languages.includes(lang) ? 'active' : ''}
              onClick={() => handleLanguageToggle(lang)}
              type="button"
            >
              {lang}
            </button>
          ))}
        </div>
      </div>

      <button onClick={handleSubmit}>提交数据</button>
    </div>
  );
};

export default ManualInput;
