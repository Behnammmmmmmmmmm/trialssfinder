import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { subscriptionsAPI } from '../api/subscriptions';
import { PaymentMethod, Subscription } from '../types';

export const SubscriptionPage: React.FC = () => {
  const { trialId } = useParams<{ trialId?: string }>();
  const navigate = useNavigate();
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethod[]>([]);
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [invoices, setInvoices] = useState<any[]>([]);
  const [address, setAddress] = useState('');
  const [newMethod, setNewMethod] = useState({
    method_type: 'credit_card',
    last_four: '',
    is_default: false
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const methodsRes = await subscriptionsAPI.getPaymentMethods();
      setPaymentMethods(methodsRes.data);

      const subsRes = await subscriptionsAPI.getSubscriptions();
      setSubscriptions(subsRes.data);

      const invoicesRes = await subscriptionsAPI.getInvoices();
      setInvoices(invoicesRes.data);
    } catch (error) {
      console.error('Failed to load subscription data:', error);
    }
  };

  const handleAddPaymentMethod = async () => {
    try {
      await subscriptionsAPI.addPaymentMethod(newMethod);
      loadData();
      setNewMethod({ method_type: 'credit_card', last_four: '', is_default: false });
    } catch (error) {
      console.error('Failed to add payment method:', error);
    }
  };

  const handleDeleteMethod = async (id: number) => {
    try {
      await subscriptionsAPI.deletePaymentMethod(id);
      loadData();
    } catch (error) {
      console.error('Failed to delete payment method:', error);
    }
  };

  const handleSetDefault = async (id: number) => {
    try {
      await subscriptionsAPI.setDefaultPaymentMethod(id);
      loadData();
    } catch (error) {
      console.error('Failed to set default payment method:', error);
    }
  };

  const handleUpdateAddress = async () => {
    try {
      await subscriptionsAPI.updateAddress(address);
      alert('Address updated');
    } catch (error) {
      console.error('Failed to update address:', error);
    }
  };

  const handlePayment = async (methodId: number) => {
    if (!trialId) {
      return;
    }
    try {
      await subscriptionsAPI.createSubscription({
        trial_id: parseInt(trialId),
        payment_method_id: methodId
      });
      navigate('/payment-success');
    } catch (error) {
      console.error('Payment failed:', error);
    }
  };

  if (trialId) {
    return (
      <div>
        <h1>Payment for Trial</h1>
        <h3>Select Payment Method</h3>
        {paymentMethods.map(method => (
          <div key={method.id}>
            <span>{method.method_type} ending in {method.last_four}</span>
            <button onClick={() => handlePayment(method.id)}>Pay with this method</button>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div>
      <h1>Subscription Management</h1>

      <h2>Your Subscriptions</h2>
      {subscriptions.map(sub => (
        <div key={sub.id}>
          <h3>{sub.trial_name}</h3>
          <p>Amount: ${sub.amount}</p>
          <p>Status: {sub.status}</p>
          <p>Date: {sub.created_at}</p>
        </div>
      ))}

      <h2>Address</h2>
      <input
        type="text"
        value={address}
        onChange={(e) => setAddress(e.target.value)}
        placeholder="Address"
      />
      <button onClick={handleUpdateAddress}>Update Address</button>

      <h2>Payment Methods</h2>
      {paymentMethods.map(method => (
        <div key={method.id}>
          <span>{method.method_type} ending in {method.last_four}</span>
          {method.is_default && <span> (Default)</span>}
          <button onClick={() => handleSetDefault(method.id)}>Make Default</button>
          <button onClick={() => handleDeleteMethod(method.id)}>Remove</button>
        </div>
      ))}

      <h3>Add Payment Method</h3>
      <select 
        value={newMethod.method_type} 
        onChange={(e) => setNewMethod({...newMethod, method_type: e.target.value})}
      >
        <option value="credit_card">Credit Card</option>
        <option value="paypal">PayPal</option>
      </select>
      <input
        type="text"
        value={newMethod.last_four}
        onChange={(e) => setNewMethod({...newMethod, last_four: e.target.value})}
        placeholder="Last 4 digits"
        maxLength={4}
      />
      <label>
        <input
          type="checkbox"
          checked={newMethod.is_default}
          onChange={(e) => setNewMethod({...newMethod, is_default: e.target.checked})}
        />
        Set as default
      </label>
      <button onClick={handleAddPaymentMethod}>Add</button>

      <h2>Invoices</h2>
      {invoices.map(invoice => (
        <div key={invoice.id}>
          <p>Amount: ${invoice.amount}</p>
          <p>Date: {invoice.created_at}</p>
        </div>
      ))}
    </div>
  );
};

export default SubscriptionPage;