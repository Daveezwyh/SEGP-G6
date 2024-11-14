const TOKENKEY = 'token_key'

function setToken(token){
    return window.localStorage.setItem(TOKENKEY, token)
}

function getToken(){
    return window.localStorage.getItem(TOKENKEY)
}

function removeToken(){
    return window.localStorage.removeItem(TOKENKEY)
}

export {
    setToken,
    getToken,
    removeToken
}