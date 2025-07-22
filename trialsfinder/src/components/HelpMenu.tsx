import React, { useState } from 'react';
import { Link } from 'react-router-dom';

export const HelpMenu: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div>
      <button onClick={() => setIsOpen(!isOpen)}>?</button>
      {isOpen && (
        <div>
          <Link to="/faq">FAQ</Link>
          <Link to="/contact">Contact Us</Link>
          <Link to="/about">About Us</Link>
          <Link to="/terms">Terms of Use</Link>
          <Link to="/privacy">Privacy Policy</Link>
        </div>
      )}
    </div>
  );
};

export default HelpMenu;