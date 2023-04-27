import { useRef, useState } from "react"
import styles from "../styles/Registration.module.css"
import axios from "axios"

const baseUrl = "localhost"
export default function RegistrationPage(){
    const ref = useRef(null)
    const [inputs, setInputs] = useState({});

    function handleChange(event){
      const name = event.target.name;
      const value = event.target.value;
      setInputs(values => ({...values, [name]: value}))
    }
  
    const handleSubmit = (event) => {
      event.preventDefault();
      if(isFormValid(inputs)){
        registerNewUser(inputs)
      }else{
        alert("You didn't fill out the form properly. Try again.");
      }
    }
    return <div className={styles.registrationDiv}>
            <form className={styles.registrationForm} onSubmit={handleSubmit}>
                <div className={styles.titleDiv}>
                    <h1>Register on <i>LightningGallery</i></h1>
                    <p>Enter your profile information here.</p>
                </div>
                <div className={`${styles.nameDiv} ${styles.inputDiv}`}>
                    <div className={styles.innerNameDiv}>
                        <input className={styles.inputField} name="name" value={inputs.name || ""} onChange={handleChange} placeholder="Name"></input>
                    </div>
                    <div>
                        <input className={styles.inputField} name="surname" value={inputs.surname || ""} onChange={handleChange} placeholder="Surame"></input>
                    </div>
                </div>
                <div className={styles.inputDiv}>
                    <input className={styles.inputField} type="text" name="birthday" value={inputs.birthday || ""} onChange={handleChange} placeholder="Birthday"
                    ref={ref}
                        onFocus={() => (ref.current.type = "date")}
                        onBlur={() => (ref.current.type = "text")}></input>
                </div>
                <div className={styles.inputDiv}>
                    <input className={styles.inputField} name="username" value={inputs.username || ""} onChange={handleChange} placeholder="Username"></input>
                </div>
                <div className={styles.inputDiv}>
                    <input className={styles.inputField} type="email" name="email" value={inputs.email || ""} onChange={handleChange} placeholder="Email"></input>
                </div>
                <div className={styles.inputDiv}>
                    <input className={styles.inputField} type="password" name="password" value={inputs.password || ""} onChange={handleChange} placeholder="Password"></input>
                </div>
                <div className={styles.inputDiv}>
                    <div className={styles.submitDiv}>
                        <input className={styles.submitBtn} type="submit" value="Register"/>
                    </div>
                </div>
            </form>
        </div>
} 

function isFormValid(inputs){
    const requiredFields = ['name', 'surname', 'birthday','username', 'email', 'password'];
    if(Object.keys(inputs).length < 6 || Object.values(inputs).includes(" ")){
        return false;
    }

    return true;
}

function registerNewUser(inputs){
    axios.post(baseUrl, {'newUser':inputs}).then((response) => {Console.log(response.data)}).catch((err) => {Console.log(err)})
}