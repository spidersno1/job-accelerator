import React from 'react';
import { Radar } from 'react-chartjs-2';
import { Chart as ChartJS, RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend } from 'chart.js';
import api from '../lib/api';
import { Skill } from '../types/index';

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

interface SkillsRadarProps {
  skills: Skill[];
}

export const SkillsRadar: React.FC<SkillsRadarProps> = ({ skills }) => {
  const data = {
    labels: skills.map(skill => skill.skill_name),
    datasets: [
      {
        label: '技能水平',
        data: skills.map(skill => skill.proficiency_level),
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 2,
      },
    ],
  };

  const options = {
    scales: {
      r: {
        angleLines: {
          display: true,
        },
        suggestedMin: 0,
        suggestedMax: 100,
      },
    },
  };

  return <Radar data={data} options={options} />;
};

export const UserSkillsRadar: React.FC = () => {
  
  const [skills, setSkills] = React.useState<Skill[]>([]);

  React.useEffect(() => {
    const fetchSkills = async () => {
      try {
        const response = await api.get('/skills/');
        setSkills(response.data);
      } catch (error) {
        console.error('Failed to fetch skills:', error);
      }
    };

    fetchSkills();
  }, [api]);

  return <SkillsRadar skills={skills} />;
};
