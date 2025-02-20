import React from 'react';
import { createBrowserRouter } from 'react-router-dom';

import Login from '../pages/Login';
import Register from '../pages/Register';
import Homepage from '../pages/Homepage';
import ProgressBar from '../pages/Homepage/bars/ProgressBar';

import { AuthRoute } from '../components/AuthRoute';

const router = createBrowserRouter([
    {
        path: "/",
        element: <Login />
    },
    {
        path: "/register",
        element: <Register />
    },
    {
        path: "/homepage",
        element: <AuthRoute><Homepage /></AuthRoute>
    },
    {
        path: "/progressbar",
        element: <ProgressBar />
    },
]);

export default router;