import React, { useEffect, useState } from 'react';
import { companiesAPI } from '../api/companies';

export const CompanyProfilePage: React.FC = () => {
  const [formData, setFormData] = useState({
    name: '',
    address: '',
    phone: '',
    website: ''
  });

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const response = await companiesAPI.getProfile();
      setFormData(response.data);
    } catch (error) {
      console.error('Failed to load company profile:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await companiesAPI.updateProfile(formData);
      alert('Profile updated successfully');
    } catch (error) {
      console.error('Failed to update profile:', error);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div>
      <h1>Company Profile</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          name="name"
          value={formData.name}
          onChange={handleChange}
          placeholder="Company Name"
        />
        <input
          type="text"
          name="address"
          value={formData.address}
          onChange={handleChange}
          placeholder="Address"
        />
        <input
          type="text"
          name="phone"
          value={formData.phone}
          onChange={handleChange}
          placeholder="Phone"
        />
        <input
          type="url"
          name="website"
          value={formData.website}
          onChange={handleChange}
          placeholder="Website"
        />
        <button type="submit">Save</button>
      </form>
    </div>
  );
};

export default CompanyProfilePage;