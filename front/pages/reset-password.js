import styles from "../styles/Login.module.css"
import { useRouter } from "next/router";
import UserPool from "@/helper/UserPool";
import { AuthenticationDetails, CognitoUser } from "amazon-cognito-identity-js";
import { useState } from "react";

export default function LoginPage() {
    const router = useRouter();
    const [credentialsNotValid, setCredentialsNotValid] = useState();

    const handleSubmit = (event) => {
        event.preventDefault();
        const username = event.currentTarget.username.value;
        const password = event.currentTarget.password.value;
        if (username == '' || password == '') {
            alert("You didn't fill out the form properly. Try again.");
        } else {
            resetPassword({ username: username, password: password }, router, setCredentialsNotValid)
        }
    }
    return <div className={styles.registrationDiv}>
        <form className={styles.registrationForm} onSubmit={handleSubmit}>
            <div className={styles.titleDiv}>
                <h1>Reset password</h1>
            </div>

            <div className={styles.inputDiv}>
                <input className={styles.inputField} type="text" id="username" name="username" placeholder="Email" />
            </div>
            <div className={styles.inputDiv}>
                <input className={styles.inputField} type="password" id="password" name="password" placeholder="Password" />
            </div>
            <div className={styles.inputDiv}>
                <div className={styles.submitDiv}>
                    <input className={styles.submitBtn} type="submit" value="Login" />
                </div>
            </div>
            {credentialsNotValid && <p className="err">Credentials not valid. Try again.</p>}
        </form>
    </div>
}

function resetPassword(credentials, router, setCredentialsNotValid) {

}