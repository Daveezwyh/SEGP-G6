import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import Header from "./Header.jsx"
import Body from "./body.jsx"
import React from 'react';

export default function Homepage() {
    return (
        <div className="min-h-screen dark:bg-slate-700">
            <Header />
            <Body />

        </div>
    );
}
