import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { trialsAPI } from '../api/trials';
import { Industry } from '../types';

export const CreateTrialPage: React.FC = () => {
  const navigate = useNavigate();
  const [industries, setIndustries] = useState<Industry[]>([]);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    industry: '',
    location: '',
    start_date: '',
    end_date: ''
  });

  useEffect(() => {
    loadIndustries();
  }, []);

  const loadIndustries = async () => {
    try {
      const response = await trialsAPI.getIndustries();
      setIndustries(response.data);
    } catch (error) {
      console.error('Failed to load industries:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await trialsAPI.create(formData);
      navigate(`/payment/${response.data.id}`);
    } catch (error) {
      console.error('Failed to create trial:', error);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div>
      <h1>Create Trial</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          name="title"
          value={formData.title}
          onChange={handleChange}
          placeholder="Title"
        />
        <textarea
          name="description"
          value={formData.description}
          onChange={handleChange}
          placeholder="Description"
        />
        <select name="industry" value={formData.industry} onChange={handleChange}>
          <option value="">Select Industry</option>
          {industries.map(industry => (
            <option key={industry.id} value={industry.id}>{industry.name}</option>
          ))}
        </select>
        <input
          type="text"
          name="location"
          value={formData.location}
          onChange={handleChange}
          placeholder="Location"
        />
        <input
          type="date"
          name="start_date"
          value={formData.start_date}
          onChange={handleChange}
        />
        <input
          type="date"
          name="end_date"
          value={formData.end_date}
          onChange={handleChange}
        />
        <button type="submit">Create Trial</button>
      </form>
    </div>
  );
};

export default CreateTrialPage;