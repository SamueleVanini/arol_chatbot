import React, {useContext, useState} from 'react';

const AuthContext = React.createContext();

export const Authorization = {
    Authorized: 'authorized',
    Unauthorized: 'unauthorized',
};

export function AuthProvider({children}) {

    const [authenticatedStatus, setAuthenticatedStatus] = useState(() => {
        // Check for token on initial load
        return localStorage.getItem('token')
            ? Authorization.Authorized
            : Authorization.Unauthorized;
    });


    const login = (token) => {
        setAuthenticatedStatus(Authorization.Authorized);
        localStorage.setItem('token', token);
    }

    const logout = () => {
        setAuthenticatedStatus(Authorization.Unauthorized);
        // Clear the token from local storage or any other storage mechanism
        localStorage.removeItem('token');
        // Optionally, you can also clear other user-related data
        localStorage.removeItem('user');
        // Redirect to login page or home page
        window.location.href = '/login';
    }

    return (
        <AuthContext.Provider value={{authenticatedStatus: authenticatedStatus, login, logout}}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    return useContext(AuthContext);
}
