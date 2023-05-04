import styles from "../styles/Login.module.css"
import axios from "axios"
import { baseUrl } from "./_app"
import { useRouter } from "next/router";

export default function LoginPage() {
    const router = useRouter();

    const handleSubmit = (event) => {
        event.preventDefault();
        const username = event.currentTarget.username.value;
        const password = event.currentTarget.password.value;
        if (username == '' || password == '') {
            alert("You didn't fill out the form properly. Try again.");
        } else {
            login({ username: username, password: password }, router)
        }
    }
    return <div className={styles.registrationDiv}>
        <form className={styles.registrationForm} onSubmit={handleSubmit}>
            <div className={styles.titleDiv}>
                <h1>Login to <i>LightningGallery</i></h1>
                <p>Enter your profile information here.</p>
            </div>

            <div className={styles.inputDiv}>
                <input className={styles.inputField} type="text" id="username" name="username" placeholder="Username" />
            </div>
            <div className={styles.inputDiv}>
                <input className={styles.inputField} type="password" id="password" name="password" placeholder="Password" />
            </div>
            <div className={styles.inputDiv}>
                <div className={styles.submitDiv}>
                    <input className={styles.submitBtn} type="submit" value="Login" />
                </div>
            </div>
        </form>
    </div>
}

function login(credentials, router) {
    axios.post(`${baseUrl}/api/login`, credentials).then((response) => { localStorage.setItem('user', JSON.stringify(response.data)); router.replace('/') }).catch((err) => { alert(err) });
}