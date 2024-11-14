import { Form, Input, Button, message } from 'antd';
import './index.scss';
import { Link, useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { fetchLogin } from '../../store/modules/user';

const Login = () => {
    const dispatch = useDispatch();
    const navigate = useNavigate();

    const onFinish = async (values) => {
        console.log(values);
        try {
            const isLoginSuccessful = await dispatch(fetchLogin(values));
    
            if (isLoginSuccessful) {

                navigate('/homepage');
                message.success('Login Successfully!');
            } else {
                message.error('Login failed. Please check your username and password.');
            }
        } catch (error) {
            message.error('An error occurred during login.');
        }
    };    

    return (
        <div className="login">
            <div className="rectangle-background">
                <div className="rectangle1"></div>
                <div className="rectangle2"></div>
                <div className="logo"></div>
            </div>

            <div className="login-container">
                <div className="login-form">
                    
                        <Form onFinish={onFinish} validateTrigger="onBlur">
                            <h1>LOG IN</h1>

                            {/* Username Input */}
                            <span className="input-tips">Username</span>
                            <Form.Item
                                className="input-item"
                                name="username"
                                rules={[{ required: true, message: 'Please input your username!' }]}
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

                            {/* Submit Button */}
                            <Form.Item>
                                <Button className="button" type="primary" htmlType="submit" size="large" block>
                                    Login
                                </Button>
                            </Form.Item>

                            {/*Sign Up*/}
                            <div className="sign-up">
                                <span>Don't Have An Account? </span>
                                <Link to="/register">Sign up</Link>
                            </div>
                        </Form>
                </div>
            </div>
        </div>
    );
};

export default Login;