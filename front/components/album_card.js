import { useState } from "react"
import styles from "../styles/AlbumCard.module.css"
import Image from "next/image"

export default function AlbumCard() {
    const [preview, setPreview] = useState(false)
    return <div className={styles.card_container}>
        <div className={styles.card}>
            <div className={styles.card_nav}>
                <h3>Main album</h3>
            </div>
            {preview ? <DocumentPreview /> :
                <div className={styles.grid}>
                    <AlbumDocument setPreview={setPreview} noBorderTop={true} noBorderLeft={true} />
                    <AlbumDocument setPreview={setPreview} noBorderTop={true} />
                    <AlbumDocument setPreview={setPreview} noBorderTop={true} />
                    <AlbumDocument setPreview={setPreview} noBorderLeft={true} />
                    <AlbumDocument setPreview={setPreview} />
                    <AlbumDocument setPreview={setPreview} />
                </div>}
        </div>
    </div>

}

function AlbumDocument({ noBorderTop, noBorderLeft, setPreview }) {
    return <div className={!noBorderLeft && styles.border_left} onClick={() => setPreview(true)}>
        <div className={styles.document}>
            <div>
                <Image src={'/images/document.png'} width={30} height={30} alt="doc" />
            </div>
            <div className={`${styles.file_data} ${!noBorderTop && styles.border_top}`}>
                <h4>Ime fajla</h4>
                <p> tip</p></div>
        </div>
    </div>
}

function DocumentPreview() {
    return <div>
        <div>
            <Image src={'/images/document.png'} width={300} height={300} alt="doc" ></Image>
        </div>
        <h4>Name</h4>
        <div>description</div>
        <div>tags</div>
    </div>
}