import styles from "@/styles/Home.module.css"
import { useEffect, useState } from "react"
import Image from "next/image";

var user = {}

export default function Home() {

  useEffect(() => {
    user = localStorage.getItem('user')
  }, []);

  return <>
    <Grid />
  </>
}

function Grid() {
  return <div className={styles.grid}>
    <ProfileCard />
    <UploadDocumentCard />
  </div>
}

function ProfileCard() {
  const numberOfAvatars = 7;
  const [avatarIndex, setAvatarIndex] = useState(user && user['avatar'] ? user['avatar'] : get_new_random_avatar());

  function get_new_random_avatar() {
    return `${Math.random() < 0.5 ? 'm' : 'f'}${Math.floor(Math.random() * numberOfAvatars)}`;
  }

  function assign_new_avatar(new_avatar_name) {
    user['avatar'] = new_avatar_name;
    setAvatarIndex(new_avatar_name);
    // Upisi u bazu
  }

  return <div className={`${styles.card} ${styles.card_small}`}>
    <div className={styles.card_body}>
      <div className={styles.avatar_section}>
        <div>
          <Image src={`/images/characters/${avatarIndex}.png`} alt="Avatar" width={120} height={120} />
        </div>
        <div onClick={() => assign_new_avatar(get_new_random_avatar())}>
          <Image src={`/images/reset.png`} alt="Avatar" width={30} height={30} />
        </div>
      </div>
      <div>
        <h2>{user['username'] || 'Anonimus'}</h2>
      </div>
      <div>
        <h4>{user['email'] || ''}</h4>
      </div>
      <div>
        <h5>{`${user['name'] || ''} ${user['surname'] || ''}`}</h5>
      </div>
    </div>
  </div>
}

function UploadDocumentCard() {
  return <div className={`${styles.card} ${styles.card_large}`}>
    <div className={styles.card_nav}>
      <h3>Upload</h3>
    </div>

  </div>
}