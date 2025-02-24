import React from 'react';
import { createBrowserRouter } from 'react-router-dom';

import Login from '../pages/Login';
import Register from '../pages/Register';
import Homepage from '../pages/Homepage';
import InfoPage from '../pages/InfoPage/Information';

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
        path: "/info",
        element: <AuthRoute><InfoPage /></AuthRoute>
    },
]);

export default router;