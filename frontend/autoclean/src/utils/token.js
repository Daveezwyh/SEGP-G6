const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

function setToken(access, refresh) {
    console.log('Saving tokens:', access, refresh);
    if (access) {
        window.localStorage.setItem(ACCESS_TOKEN_KEY, access);
    }
    if (refresh) {
        window.localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
    }
}

function getToken() {
    return window.localStorage.getItem(ACCESS_TOKEN_KEY);
}

function getRefreshToken() {
    return window.localStorage.getItem(REFRESH_TOKEN_KEY);
}

function removeToken() {
    window.localStorage.removeItem(ACCESS_TOKEN_KEY);
    window.localStorage.removeItem(REFRESH_TOKEN_KEY);
}

export { setToken, getToken, getRefreshToken, removeToken };