import React from 'react';
import { message } from 'antd';
import { Form, Input, Button } from 'antd';
import './index.scss';
import axios from 'axios';
import { Link, useNavigate } from 'react-router-dom';

const Register = () => {
    const navigate = useNavigate();

    const onFinish = async (values) => {
        console.log(values);
        try {
            const response = await axios.post('http://35.213.150.144:8000/api/users/', values);
            console.log('Registration successful:', response.data);
            message.success('Registration successful!');
            navigate('/');
        } catch (error) {
            console.error('Registration failed:', error.response ? error.response.data : error.message);
            message.error('Registration failed: ' + (error.response ? error.response.data.detail || 'Unknown error' : error.message));
        }
    };

    //Validate Password
    const validateConfirmPassword = ({ getFieldValue }) => ({
        validator(_, value) {
            if (!value || getFieldValue('password') === value) {
                return Promise.resolve();
            }
            return Promise.reject(new Error('The two passwords that you entered do not match!'));
        }
    });

    return (
        <div className="register">
            <div className="rectangle-background">
                <div className="rectangle1"></div>
                <div className="rectangle2"></div>
                <div className="logo"></div>
            </div>

            <div className="register-container">
                <div className="register-form">

                        <Form onFinish={onFinish} validateTrigger="onBlur">
                            <h1>Register</h1>

                            {/* Username Input */}
                            <span className="input-tips">Username</span>
                            <Form.Item
                                className="input-item"
                                name="username"
                                rules={[{required: true,message: 'Please input your username!'}]}
                                hasFeedback
                            >
                                <Input size="large" placeholder="Please enter your username" />
                            </Form.Item>

                            {/* Password Input */}
                            <span className="input-tips">Password</span>
                            <Form.Item
                                className="input-item"
                                name="password"
                                rules={[{ required: true, message: 'Please input your password!' }]}
                                hasFeedback
                            >
                                <Input.Password size="large" placeholder="Please enter your password" />
                            </Form.Item>

                            {/* Confirm Password Input */}
                            <span className="input-tips">Password Confirmation</span>
                            <Form.Item
                                className="input-item"
                                name="confirm"
                                rules={[{ required: true, message: 'Please confirm your password!' }, validateConfirmPassword]}
                                hasFeedback
                            >
                                <Input.Password size="large" placeholder="Please confirm your password!" />
                            </Form.Item>
                            
                            {/* Submit Button */}
                            <Form.Item>
                                <Button className='button' type="primary" htmlType="submit" size="large" block>
                                    Register
                                </Button>
                            </Form.Item>

                            {/*Have an account*/}
                            <div className="have-account">
                                <span>Already have an account? </span>
                                <Link to ="/">Please log in</Link>
                            </div>

                        </Form>
                    </div>
            </div>
        </div>
    );
};

export default Register;