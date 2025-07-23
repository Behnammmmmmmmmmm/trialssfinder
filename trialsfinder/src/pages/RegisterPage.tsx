import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useStore';

export const RegisterPage: React.FC = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    user_type: 'user' as 'user' | 'company',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.email.includes('@')) {
      newErrors.email = 'Please enter a valid email';
    }

    if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    // Only validate confirm password for company accounts
    if (formData.user_type === 'company' && formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    setLoading(true);
    try {
      const registrationData: any = {
        email: formData.email,
        password: formData.password,
        user_type: formData.user_type,
      };

      // Only include confirm_password for company registration
      if (formData.user_type === 'company') {
        registrationData.confirm_password = formData.confirmPassword;
      }

      await register(registrationData);
      navigate('/verify-email');
    } catch (error) {
      setErrors({ general: 'Registration failed. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    if (name === 'user_type') {
      setFormData({ ...formData, [name]: value as 'user' | 'company' });
    } else {
      setFormData({ ...formData, [name]: value });
    }
    // Clear error for this field
    if (errors[name]) {
      setErrors({ ...errors, [name]: '' });
    }
  };

  return (
    <div className="container min-h-screen flex items-center justify-center py-12">
      <div className="card shadow-xl" style={{ maxWidth: '500px', width: '100%' }}>
        <div className="card-body">
          <h1 className="text-3xl font-bold text-center mb-6">Create Account</h1>
          <p className="text-center text-muted mb-6">Join TrialsFinder today</p>

          {errors.general && (
            <div className="alert mb-4" data-variant="danger">
              {errors.general}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="email" className="form-label">
                Email
              </label>
              <input
                id="email"
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="your@email.com"
                className={`form-control ${errors.email ? 'border-danger' : ''}`}
                required
                disabled={loading}
              />
              {errors.email && <p className="text-danger text-sm mt-1">{errors.email}</p>}
            </div>

            <div className="form-group">
              <label htmlFor="password" className="form-label">
                Password
              </label>
              <input
                id="password"
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Create a strong password"
                className={`form-control ${errors.password ? 'border-danger' : ''}`}
                required
                disabled={loading}
              />
              {errors.password && <p className="text-danger text-sm mt-1">{errors.password}</p>}
            </div>

            {/* Only show confirm password for company accounts */}
            {formData.user_type === 'company' && (
              <div className="form-group">
                <label htmlFor="confirmPassword" className="form-label">
                  Confirm Password
                </label>
                <input
                  id="confirmPassword"
                  type="password"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  placeholder="Confirm your password"
                  className={`form-control ${errors.confirmPassword ? 'border-danger' : ''}`}
                  required
                  disabled={loading}
                />
                {errors.confirmPassword && (
                  <p className="text-danger text-sm mt-1">{errors.confirmPassword}</p>
                )}
              </div>
            )}

            <div className="form-group">
              <label htmlFor="user_type" className="form-label">
                Account Type
              </label>
              <select
                id="user_type"
                name="user_type"
                value={formData.user_type}
                onChange={handleChange}
                className="form-control"
                disabled={loading}
              >
                <option value="user">Individual User</option>
                <option value="company">Company</option>
              </select>
              <p className="text-sm text-muted mt-1">
                Choose "Company" if you want to list trials
              </p>
            </div>

            <button
              type="submit"
              className="btn w-full mb-4"
              data-variant="primary"
              data-size="lg"
              disabled={loading}
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <span className="spinner mr-2"></span>
                  Creating Account...
                </span>
              ) : (
                'Create Account'
              )}
            </button>
          </form>

          <div className="text-center">
            <p className="text-muted">
              Already have an account?{' '}
              <a href="/login" className="text-primary hover:underline">
                Sign In
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;