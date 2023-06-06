import UserPool from '@/helper/UserPool';
import { getUserAccessToken, getUserRefreshToken, logOut } from '@/helper/helper';
import '@/styles/globals.css'
import axios from 'axios';

// export const baseUrl = "http://127.0.0.1:3000";
export const baseUrl = "https://51n00aok1m.execute-api.eu-central-1.amazonaws.com/Prod";

axios.interceptors.request.use(
  config => {
    const token = getUserAccessToken();
    if (token && !config.headers['skip']) {
      config.headers['Authorization'] = 'Bearer ' + token
    }
    // config.headers['Content-Type'] = 'application/json';
    return config
  },
  error => {
    Promise.reject(error)
  }
)

axios.interceptors.response.use(
  response => {
    return response;
  },
  async function (error) {
    const originalRequest = error.config;

    if (error.response && error.response.status === 401) {
      originalRequest._retry = true;
      const tokenEndpoint = 'https://cloud-users-ftn.auth.eu-central-1.amazoncognito.com/oauth2/token';
      const clientId = UserPool.getClientId();
      const refreshToken = getUserRefreshToken();

      return axios.post(tokenEndpoint, {
        grant_type: 'refresh_token',
        client_id: clientId,
        refresh_token: refreshToken
      }, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'skip': 'true'
        },
        transformRequest: [function (data, headers) {
          return Object.entries(data).map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`).join('&');
        }]
      }).then(response => {
        if (response.status === 200) {
          localStorage.setItem('accessToken', response.data.access_token);
          localStorage.setItem('idToken', response.data.id_token);
          axios.defaults.headers.common['Authorization'] =
            'Bearer ' + getUserAccessToken();
          return axios(originalRequest);
        } else {
          logOut();
        }
      }).catch(err => {
        logOut();
      });
    }
    return Promise.reject(error)
  }
)

export default function App({ Component, pageProps }) {
  return <Component {...pageProps} />
}
