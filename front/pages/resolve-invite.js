import { getQueryVariable } from "@/helper/helper";
import axios from "axios";
import { useEffect, useState } from "react"
import { baseUrl } from "./_app";
import styles from "@/styles/"

export default function Invite() {
    const [action, setAction] = useState();
    const [invite, setInvite] = useState();
    const [success, setSuccess] = useState(false);
    const [err, setErr] = useState(false);
    useEffect(() => {
        action = getQueryVariable('action');
        invite = getQueryVariable('invite');
        sendInviteResponse(action, invite);
        setAction(action);
        setInvite(invite);
    }, []);

    function sendInviteResponse(action, invite) {
        axios.put(`${baseUrl}/api/resolveInvitation`, { 'action': action, 'invite': invite }).then(response => setSuccess(true)).catch(err => setErr(true));
    }

    return <div className="container">
        <h1>Invitation</h1>
        {success ? <div>
            {action == 'accept' ? <p className="success">{`You have granted access to your files to ${invite.split(',')[0]}`}</p> : <p className="err">{`You have denied access to your files to ${invite.split(',')[0]}`}</p>}
        </div> : <span className={styles.loader}></span>}
    </div>
}