import { Form, Input, Button } from 'antd';
import './index.scss';
import axios from 'axios';
import { Link, useNavigate } from 'react-router-dom';

const Register = () => {
    const navigate = useNavigate();

    const onFinish = async (values) => {
        console.log(values);
        try {
            const response = await axios.post('', values);
            console.log('Registration successful:', response.data);
            // Jumping to the login page
            navigate('/');
        } catch (error) {
            console.error('Registration failed:', error.response ? error.response.data : error.message);
            // Handle errors, such as displaying error messages
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
            <div className="register-container">

                {/* Image */}
                <div className="left-img">
                    <div className="glass">
                        <div className="tips">
                            <div className="title">DATA CLEANING</div>
                            <h1>Clean up all garbage data</h1>
                            <span>5 Million+ people have chosen our tool. </span>
                            <span>We invite you to join us!</span>
                        </div>
                    </div>
                </div>

                {/* Login Form */}
                <div className="register-form">
                    <div className="form-wrapper">

                        <Form onFinish={onFinish} validateTrigger="onBlur">
                            <h1>Register</h1>

                            {/* Email Input */}
                            <span className="input-tips">Email Address</span>
                            <Form.Item
                                className="input-item"
                                name="email"
                                rules={[
                                    {
                                        required: true,
                                        message: 'Please input your email address!'
                                    },
                                    {
                                        pattern: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
                                        message: 'Please enter a valid email address!'
                                    }
                                ]}
                                hasFeedback
                            >
                                <Input size="large" placeholder="Please enter your email address" />
                            </Form.Item>

                            {/* Password Input */}
                            <span className="input-tips">Password</span>
                            <Form.Item
                                className="input-item"
                                name="password"
                                rules={[
                                    { 
                                        required: true, 
                                        message: 'Please input your password!' 
                                    },
                                    {
                                        pattern: /^.{8,20}$/,
                                        message: 'Password must be between 8 to 20 characters.'
                                    }
                                ]}
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
                                <span>Already have an account?</span>
                                <Link to ="/">Please log in</Link>
                            </div>

                        </Form>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Register;