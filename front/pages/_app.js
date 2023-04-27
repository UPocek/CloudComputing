import '@/styles/globals.css'

export const baseUrl = "http://localhost:3000";

export default function App({ Component, pageProps }) {
  return <Component {...pageProps} />
}
