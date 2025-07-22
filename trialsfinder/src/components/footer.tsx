import React from 'react';
import { Link } from 'react-router-dom';

export const Footer: React.FC = () => {
  return (
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
  );
};