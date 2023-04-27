import styles from "../styles/Login.module.css"
import axios from "axios"
import { baseUrl } from "./_app"

export default function LoginPage() {

    const handleSubmit = (event) => {
        event.preventDefault();
        const username = event.currentTarget.username.value;
        const password = event.currentTarget.password.value;
        if (username == '' || password == '') {
            alert("You didn't fill out the form properly. Try again.");
        } else {
            login({ username: username, password: password })
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
                    <input className={styles.submitBtn} type="submit" value="Register" />
                </div>
            </div>
        </form>
    </div>
}

function login(credentials) {
    axios.post(`${baseUrl}/api/login`, credentials).then((response) => { console.log(response.data) }).catch((err) => { console.log(err) })
}