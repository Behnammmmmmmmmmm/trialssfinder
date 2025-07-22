import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { authAPI } from '../api/auth';

export const ForgotPasswordPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await authAPI.forgotPassword(email);
      setSubmitted(true);
    } catch (error) {
      console.error('Failed to send reset link:', error);
    }
  };

  if (submitted) {
    return (
      <div>
        <h1>Reset Link Sent</h1>
        <p>If your email is associated with an account, you'll receive a link to reset your password.</p>
        <Link to="/login">Back to Login</Link>
      </div>
    );
  }

  return (
    <div>
      <h1>Forgot Password</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Enter your email"
        />
        <button type="submit">Send Reset Link</button>
      </form>
      <Link to="/login">Back to Login</Link>
    </div>
  );
};

export default ForgotPasswordPage;