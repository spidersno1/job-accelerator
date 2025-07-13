import { LeetCodeData } from './LeetCodeAnalysis';
import { Bar, Pie } from 'react-chartjs-2';
import { Chart as ChartJS, registerables } from 'chart.js';
import { useEffect } from 'react';

ChartJS.register(...registerables);

type SkillVisualizationProps = {
  data: LeetCodeData | null;
};

const SkillVisualization = ({ data }: SkillVisualizationProps) => {
  useEffect(() => {
    return () => {
      ChartJS.unregister(...registerables);
    };
  }, []);

  if (!data) {
    return <div className="no-data">暂无数据</div>;
  }

  const difficultyData = {
    labels: ['简单', '中等', '困难'],
    datasets: [{
      label: '题目数量',
      data: [data.stats.easy, data.stats.medium, data.stats.hard],
      backgroundColor: [
        'rgba(75, 192, 192, 0.6)',
        'rgba(255, 206, 86, 0.6)',
        'rgba(255, 99, 132, 0.6)'
      ],
      borderColor: [
        'rgba(75, 192, 192, 1)',
        'rgba(255, 206, 86, 1)',
        'rgba(255, 99, 132, 1)'
      ],
      borderWidth: 1
    }]
  };

  const languageData = {
    labels: data.languages,
    datasets: [{
      label: '使用语言',
      data: data.languages.map(lang => {
        return Math.floor(Math.random() * 50) + 20;
      }),
      backgroundColor: [
        'rgba(54, 162, 235, 0.6)',
        'rgba(255, 99, 132, 0.6)',
        'rgba(255, 159, 64, 0.6)',
        'rgba(153, 102, 255, 0.6)',
        'rgba(75, 192, 192, 0.6)'
      ],
      borderWidth: 1
    }]
  };

  return (
    <div className="skill-visualization">
      <div className="chart-container">
        <h3>题目难度分布</h3>
        <Bar data={difficultyData} />
      </div>
      <div className="chart-container">
        <h3>编程语言使用</h3>
        <Pie data={languageData} />
      </div>
    </div>
  );
};

export default SkillVisualization;
