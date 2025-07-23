import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useStore';
import { LanguageSelector } from './LanguageSelector';

export const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleUsernameClick = () => {
    if (user?.user_type === 'company') {
      navigate('/dashboard');
    } else if (user?.user_type === 'admin') {
      navigate('/admin');
    } else {
      navigate('/profile');
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      handleUsernameClick();
    }
  };

  return (
    <div className="page-container">
      <a href="#main" className="skip-link">Skip to main content</a>
      
      <header className="header" role="banner">
        <div className="header-container container">
          <Link to="/" className="text-xl font-bold text-primary" aria-label="TrialsFinder Home">
            TrialsFinder
          </Link>
          
          <nav className="header-nav" role="navigation" aria-label="Main navigation">
            <LanguageSelector />
            
            {user ? (
              <div className="flex items-center gap-4">
                <button
                  onClick={handleUsernameClick}
                  onKeyPress={handleKeyPress}
                  className="cursor-pointer text-primary font-medium transition-colors hover:text-primary-dark focus:outline-2 focus:outline-primary focus:outline-offset-2 px-2 py-1 rounded"
                  aria-label={`User menu for ${user.username}`}
                >
                  {user.username}
                </button>
                <Link
                  to="/privacy-dashboard"
                  className="header-nav-item"
                  aria-label="Privacy Settings"
                >
                  Privacy Settings
                </Link>
                <button
                  onClick={handleLogout}
                  className="btn"
                  data-variant="ghost"
                  data-size="sm"
                  aria-label="Sign out of your account"
                >
                  Sign Out
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-4">
                <Link
                  to="/login"
                  className="header-nav-item"
                  aria-label="Login to your account"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="btn"
                  data-variant="primary"
                  data-size="sm"
                  aria-label="Create a new account"
                >
                  Register
                </Link>
              </div>
            )}
          </nav>
        </div>
      </header>

      <main id="main" className="main-content" role="main">
        <div className="container">
          {children}
        </div>
      </main>

      <footer className="footer" role="contentinfo">
        <div className="container">
          <div className="footer-content">
            <div className="footer-section">
              <h2 id="footer-resources">Resources</h2>
              <nav aria-labelledby="footer-resources">
                <ul className="footer-links" role="list">
                  <li><Link to="/faq" className="footer-link">FAQ</Link></li>
                  <li><Link to="/contact" className="footer-link">Contact</Link></li>
                  <li><Link to="/about" className="footer-link">About</Link></li>
                </ul>
              </nav>
            </div>
            
            <div className="footer-section">
              <h2 id="footer-legal">Legal</h2>
              <nav aria-labelledby="footer-legal">
                <ul className="footer-links" role="list">
                  <li><Link to="/terms" className="footer-link">Terms</Link></li>
                  <li><Link to="/privacy" className="footer-link">Privacy</Link></li>
                </ul>
              </nav>
            </div>
          </div>
          
          <div className="footer-bottom">
            <p className="text-muted text-sm">© 2024 TrialsFinder. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout;