export interface User {
  id: number;
  username: string;
  email: string;
  user_type: 'user' | 'company' | 'admin';
  email_verified: boolean;
}

export interface Company {
  id: number;
  name: string;
  address: string;
  phone: string;
  website: string;
}

export interface Trial {
  id: number;
  title: string;
  description: string;
  industry: number;
  industry_name: string;
  company_name: string;
  location: string;
  start_date: string;
  end_date: string;
  status: string;
  is_featured: boolean;
  is_favorited?: boolean;
  created_at: string;  // Added this field
}

export interface Industry {
  id: number;
  name: string;
}

export interface PaymentMethod {
  id: number;
  method_type: string;
  last_four: string;
  is_default: boolean;
}

export interface Subscription {
  id: number;
  trial: number;
  trial_name: string;
  amount: string;
  status: string;
  created_at: string;
}

export interface Notification {
  id: number;
  message: string;
  is_read: boolean;
  created_at: string;
}