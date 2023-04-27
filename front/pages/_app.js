import '@/styles/globals.css'

export const baseUrl = "http://127.0.0.1:3000";

export default function App({ Component, pageProps }) {
  return <Component {...pageProps} />
}
