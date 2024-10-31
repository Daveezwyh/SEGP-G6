import Login from '../pages/Login'
import Register from '../pages/Register'
import Layout from '../pages/Layout'
import Homepage from '../pages/Homepage'

import {createBrowserRouter} from 'react-router-dom'
import { AuthRoute } from '../components/AuthRoute'

const router = createBrowserRouter([
    {
        path: "/",
        element: <Login/>
    },
    {
        path: "/register",
        element: <Register/>
    },
    {
        path: "/homepage",
        element: <Homepage/>
    },
    {
        path: "/layout",
        element: <AuthRoute><Layout/></AuthRoute>
    }
])

export default router