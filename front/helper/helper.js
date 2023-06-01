import Router from "next/router";

export function getUserRole() {
    return localStorage.getItem('userRole');
}
export function getUserAccessToken() {
    return localStorage.getItem('accessToken');
}
export function getUserIdToken() {
    return localStorage.getItem('idToken');
}
export function getUserRefreshToken() {
    return localStorage.getItem('refreshToken');
}
export function getUserEmail() {
    return parseJwt(getUserIdToken())['email'];
}
export function getUserName() {
    return parseJwt(getUserIdToken())['name'];
}
export function getUserSurname() {
    return parseJwt(getUserIdToken())['custom:surname'];
}

function parseJwt(token) {
    let jsonPayload = {}
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function (c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
    } catch (e) {
        logOut();
    }
    return JSON.parse(jsonPayload);
}

export function logOut() {
    localStorage.clear()
    Router.push('/login');
}

export function getQueryVariable(variable) {
    let query = window.location.search.substring(1);
    let vars = query.split("&");
    for (let i = 0; i < vars.length; i++) {
        let pair = vars[i].split("=");
        if (pair[0] == variable) { return pair[1]; }
    }
    return (false);
}
