import { Form, Input, Button, message } from 'antd';
import './index.scss';
import { Link, useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { fetchLogin } from '../../store/modules/user';

const Login = () => {
    const dispatch = useDispatch()
    const navigate = useNavigate()
    const onFinish = async (values) => {
        console.log(values);
        //action fetchlogin
        await dispatch(fetchLogin(values))

        navigate('/layout')

        message.success('Login Successfully!')
    };

    return (
        <div className="login">
            <div className="login-container">
                
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
                <div className="login-form">
                    <div className="form-wrapper">
                        <Form onFinish={onFinish} validateTrigger="onBlur">
                            <h1>Log in</h1>

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
                                rules={[{ required: true, message: 'Please input your password!' }]}
                                hasFeedback
                            >
                                <Input.Password size="large" placeholder="Please enter your password" />
                            </Form.Item>

                            {/* Submit Button */}
                            <Form.Item>
                                <Button className='button' type="primary" htmlType="submit" size="large" block>
                                    Login
                                </Button>
                            </Form.Item>

                            {/* Signup Link */}
                            <div className="sign-up">
                                <span>Don't Have An Account? </span>
                                <Link to = "/register">Sign up</Link>
                            </div>
                        </Form>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;