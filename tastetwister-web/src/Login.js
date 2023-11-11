import React, { useState } from 'react';
import './Login.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import { useNavigate } from "react-router-dom";


function LoginForm() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [isSignUp, setIsSignUp] = useState(false);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const navigate = useNavigate();
    

    const handleLogin = (e) => {
        e.preventDefault();
    
        if (!username || !password) {
            alert('Both fields are required!');
        } else {
            // Data to be sent in the request body
            const data = {
                username: username,
                password: password
            };
    
            // Send a POST request to the Flask login endpoint
            
            fetch('http://127.0.0.1:5000/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then((response) => response.json())
            .then((data) => {
            if (data.message === "Login successful!") {
                localStorage.setItem('username', data.username);
                console.log(localStorage.getItem('username'));
                navigate('/home')
                console.log('Successful login:', data.message);
            // Handle successful login
            } else {
                console.log('Login failed:', data.message);
                // Handle login failure
            }
        })
  .catch((error) => {
    console.error('Error:', error);
  });
        }
    };
    
    const handleSignUpClick = () => {
        setIsSignUp(true);
    };

    const handleSignUp = (e) => {
        e.preventDefault();
      
        if (!username || !password) {
          alert('Both fields are required for signup.');
        } else {
          const data = { username, password }; // Construct the data object
      
          // Send a POST request to the Flask registration endpoint
          fetch('http://127.0.0.1:5000/register', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
          })
            .then((response) => response.json())
            .then((data) => {
              if (data.message === 'Registration successful!') {
                console.log('Successful register:', data.message);
                setIsSignUp(false);
                // Handle successful registration
              } else {
                console.log('Register failed:', data.message);
                // Handle registration failure
              }
            })
            .catch((error) => {
              console.error('Error:', error);
            });
        }
      };
      
    
    return (
        <div className='wrapper d-flex align-items-center justify-content-end w-100'>
            <div className='login'>
                <h2 className='mb-3'>{isSignUp ? 'Sign Up' : 'Login Form'}</h2>
                {isSignUp ? (
                    <form onSubmit={handleSignUp}>
                        <div className='form-group mb-2'>
                            <label htmlFor='signup-username' className='form-label'>
                                Username
                            </label>
                            <input
                                type='text'
                                className='form-control'
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                            ></input>
                        </div>
                        <div className='form-group mb-2'>
                            <label htmlFor='signup-password' className='form-label'>
                                Password
                            </label>
                            <input
                                type='password'
                                className='form-control'
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            ></input>
                        </div>
                        <button type='submit' className='btn btn-success mt-2'>
                            SIGN UP
                        </button>
                    </form>
                ) : (
                    <form onSubmit={handleLogin}>
                        <div className='form-group mb-2'>
                            <label htmlFor='username' className='form-label'>
                                Username
                            </label>
                            <input
                                type='text'
                                className='form-control'
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                            ></input>
                        </div>
                        <div className='form-group mb-2'>
                            <label htmlFor='password' className='form-label'>
                                Password
                            </label>
                            <input
                                type='password'
                                className='form-control'
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                
                            ></input>
                        </div>
                        <button type='submit' className='btn btn-success mt-2'>
                            SIGN IN
                        </button>
                    </form>
                )}
                <div className='signup-text'>
                    {isSignUp ? (
                        <p>
                            Already have an account?{' '}
                            <a
                                className='link-button'
                                onClick={() => setIsSignUp(false)}
                            >
                                Sign in
                            </a>
                        </p>
                    ) : (
                        <p>
                            Don't have an account?{' '}
                            <a
                                className='link-button'
                                onClick={handleSignUpClick}
                            >
                                Sign up
                            </a>
                        </p>
                    )}
                </div>
            </div>
        </div>
    );
}

export default LoginForm;


