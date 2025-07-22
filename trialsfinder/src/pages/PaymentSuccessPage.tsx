import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export const PaymentSuccessPage: React.FC = () => {
  const navigate = useNavigate();

  useEffect(() => {
    setTimeout(() => {
      navigate('/dashboard');
    }, 1500);
  }, [navigate]);

  return (
    <div>
      <h1>🎉 Payment Successful!</h1>
      <p>Your trial is now under review.</p>
    </div>
  );
};

export default PaymentSuccessPage;