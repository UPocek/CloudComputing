import { useState } from "react"
import styles from "../styles/AlbumCard.module.css"
import Image from "next/image"

export default function AlbumCard() {
    const [preview, setPreview] = useState(false)
    const [selectedDoc, setSelectedDoc] = useState(null)
    const [documents, setDocuments] = useState([{ 'lastModified': '20.05.2023.', 'name': 'Ime dokumenta', 'tags': '#tag1;#tag2', 'comment': 'Neki koment' }, { 'lastModified': '20.05.2023.', 'name': 'Ime dokumenta', 'tags': '#tag1;#tag2', 'comment': 'Neki koment' }, { 'lastModified': '20.05.2023.', 'name': 'Ime dokumenta', 'tags': '#tag1;#tag2', 'comment': 'Neki koment' }, { 'lastModified': '20.05.2023.', 'name': 'Ime dokumenta', 'tags': '#tag1;#tag2', 'comment': 'Neki koment' }, { 'lastModified': '20.05.2023.', 'name': 'Ime dokumenta', 'tags': '#tag1;#tag2', 'comment': 'Neki koment' }, { 'lastModified': '20.05.2023.', 'name': 'Ime dokumenta', 'tags': '#tag1;#tag2', 'comment': 'Neki koment' }])

    function showPreview(index) {
        setPreview(true);
        setSelectedDoc(index);
    }

    return <div className={styles.card_container}>
        <div className={styles.card}>
            <div className={styles.card_nav}>
                <h3>Main album</h3>
            </div>
            {preview ? <DocumentPreview setPreview={setPreview} index={selectedDoc} setDocuments={setDocuments} documents={documents} /> :
                <div className={styles.grid}>
                    {documents.map((doc, index) => <AlbumDocument doc={doc} showPreview={showPreview} index={index} key={index} />)}

                </div>}
        </div>
    </div>

}

function AlbumDocument({ index, showPreview, doc }) {
    const noBorderLeft = index % 3 == 0;
    const noBorderTop = index < 3;
    return <div className={`${!noBorderLeft && styles.border_left}`} onClick={() => showPreview(index)}>
        <div className={styles.document}>
            <div>
                <Image src={'/images/document.png'} width={30} height={30} alt="doc" />
            </div>
            <div className={`${styles.file_data} ${!noBorderTop && styles.border_top}`}>
                <h4>{doc['name']}</h4>
                <p> tip</p></div>
        </div>
    </div>
}

function DocumentPreview({ index, setPreview, setDocuments, documents }) {
    const [name, setName] = useState(documents[index]['name']);
    const [tags, setTags] = useState(documents[index]['tags']);
    const [comment, setComment] = useState(documents[index]['comment']);

    const [editing, setEditing] = useState(false)

    function saveChanges(event) {
        event.preventDefault();

        const updatedDocuments = [...documents]
        updatedDocuments[index]['name'] = name;
        updatedDocuments[index]['tags'] = tags;
        updatedDocuments[index]['comment'] = comment;

        setDocuments(updatedDocuments)
        setEditing(false)
    }

    function setCurrentValues() {
        setName(documents[index]['name']);
        setTags(documents[index]['tags']);
        setComment(documents[index]['comment']);
        setEditing(false)
    }

    return <div className={styles.prev_container}>
        <div className={styles.doc_nav}>
            <div className={styles.back} onClick={() => setPreview(false)}>
                <Image src={'/images/left-arrow.png'} width={24} height={24} alt="back" ></Image>
            </div>
            <div className={styles.divider}>{documents[index]['lastModified']}</div>
            <div className={styles.divider}>
                <div className={styles.icon}>
                    <Image src={'/images/download.png'} width={30} height={30} alt="doc" ></Image>
                </div>
                <div className={styles.icon} onClick={() => setEditing(true)}>
                    <Image src={'/images/edit.png'} width={30} height={30} alt="doc" ></Image>
                </div>
                <div className={styles.icon}>
                    <Image src={'/images/delete.png'} width={30} height={30} alt="doc" ></Image>
                </div>
            </div>

        </div>
        <div className={styles.doc_body}>
            <div className={styles.doc_prev}>
                <Image src={'/images/document.png'} width={300} height={300} alt="doc" ></Image>
            </div>
            <div className={styles.doc_details}>
                <h4>{editing ? <label htmlFor="name">{`Name:`}</label> : 'Name:'}</h4>
                {editing ? <input type="name" id='name' name="name" value={name} onChange={e => setName(e.target.value)} /> : <p>{documents[index]['name']}</p>}

                <h4>{editing ? <label htmlFor="tags">{`Tags (comma-separated):`}</label> : 'Tags:'}</h4>
                {editing ? <input type="text" id='tags' name="tags" value={tags} onChange={e => setTags(e.target.value)} /> : <p>{documents[index]['tags']}</p>}

                <h4>{editing ? <label htmlFor="comment">Comment:</label> : 'Comment:'}</h4>
                {editing ? <textarea rows="4" name="comment" value={comment} onChange={e => setComment(e.target.value)} /> : <p>{documents[index]['comment']}</p>}
                {editing && <div className={styles.btns}>
                    <div className={styles.submitDiv} onClick={saveChanges}>
                        Save
                    </div>
                    <div className={`${styles.submitDiv} ${styles.cancle}`} onClick={setCurrentValues}>
                        Cancle
                    </div>
                </div>}
            </div>

        </div>

    </div>
}
