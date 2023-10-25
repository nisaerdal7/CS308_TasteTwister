import React, { useState } from 'react';
import './Login.css';
import 'bootstrap/dist/css/bootstrap.min.css';

function LoginForm() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const handleLogin = () => {
        if (username && password) {
            // Submit the data to the backend for authentication
        } else {
            alert('Both fields are required!');
        }
    };

    return (
        <div className='wrapper d-flex align-items-center justify-content-end w-100'>
            <div className = 'login' >
                <h2 className='mb-3'>Login Form</h2>
                <form>
                    <div className = 'form-group mb-2'>
                        <label htmlFor='username' className='form-label'>Username</label>
                        <input type="username" className='form-control'></input>
                    </div>
                    <div className = 'form-group mb-2'>
                        <label htmlFor='password' className='form-label'>Password</label>
                        <input type="password" className='form-control'></input>
                    </div>
                    <button type='submit' className='btn btn-success mt-2'>SIGN IN</button>
                </form>
                <div className='signup-text'>
                <p>Don't have an account? <a href='#'>Sign up</a></p>
                </div>
            </div>
         </div>
    );
}

export default LoginForm;