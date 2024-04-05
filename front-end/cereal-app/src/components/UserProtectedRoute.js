import React, { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { AuthContext } from '../contexts/auth.js';
import { jwtDecode } from 'jwt-decode';

function UserProtectedRoute({ children }) {
    // get the logged in user
    const { loggedInUser, handleContextLogin, isAdmin, setLoggedInUser } = useContext(AuthContext);

    // decode the token to get the username
    const decodedToken = loggedInUser ? jwtDecode(loggedInUser) : null;
    const username = decodedToken ? decodedToken.sub : null;
    

    // Check if the loggedInUser is an admin
    if (!loggedInUser) {
        // User not logged in, redirect to login page
        return <Navigate to="/" />;
    }

    return children;
}

export default UserProtectedRoute;