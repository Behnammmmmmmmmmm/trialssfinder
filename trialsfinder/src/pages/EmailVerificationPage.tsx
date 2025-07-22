import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../api/auth';
import { useAuth } from '../hooks/useStore';

export const EmailVerificationPage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  useEffect(() => {
    const verifyEmail = async () => {
      const token = localStorage.getItem('verification_token');
      if (token) {
        try {
          await authAPI.verifyEmail(token);
          localStorage.removeItem('verification_token');
          
          if (user?.user_type === 'company') {
            navigate('/dashboard');
          } else {
            navigate('/profile');
          }
        } catch (error) {
          console.error('Email verification failed:', error);
        }
      }
    };

    verifyEmail();
  }, [navigate, user]);

  return (
    <div>
      <h1>Verifying your email...</h1>
      <p>Please wait while we verify your email address.</p>
    </div>
  );
};

export default EmailVerificationPage;