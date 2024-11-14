import {createSlice} from '@reduxjs/toolkit'
import { request } from '../../utils'
import { setToken as _setToken, getToken } from '../../utils'
import { api_token } from '../../api'

const userStore = createSlice({
    name:"user",
    //data state
    initialState:{
        token: getToken()
    },
    //Synchronous modification method
    reducers:{
        setToken(state,action){
            state.token = action.payload
            //localstorage
            _setToken(action.payload)
        }
    }
})

const {setToken} = userStore.actions

const userReducer = userStore.reducer

//Asynchronous method to complete the login and obtain the token
const fetchLogin = (loginForm) => {
    return async (dispatch) => {
        try {
            const res = await request.post(api_token, loginForm);
            
            if (res.status === 200 && res.statusText === 'OK') {
                dispatch(setToken(res.data.token));
                return true;
            }
            return false;
        } catch (error) {
            console.error("Login request failed:", error);
            return false;
        }
    };
};

export { fetchLogin, setToken}

export default userReducer