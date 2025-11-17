import React from 'react';
import './CommonButton.css';

export default function Button({ onClick, children, variant = 'primary' }) {
    return (
        <button className={`btn ${variant}`} onClick={onClick}>
            {children}
        </button>
    );
}
