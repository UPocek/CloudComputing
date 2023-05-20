import styles from "@/styles/Home.module.css"
import { useEffect, useRef, useState } from "react"
import Image from "next/image";
import axios from "axios";
import { baseUrl } from "./_app";


export default function Home() {
  return <>
    <Grid />
  </>
}

function Grid() {
  const [user, setUser] = useState(null);
  const [albums, setAlbums] = useState(null);
  useEffect(() => {
    axios.get(`${baseUrl}/api/user`).then(response => setUser(response.data)).catch();
  }, []);
  return <>
    {user ?
      <div className={styles.grid}>
        <ProfileCard user={user} setUser={setUser} />
        <UploadDocumentCard />
        {Object.keys(user['albums']).map(albumName => <AlbumCard key={albumName} albumName={albumName} album={user['albums'][albumName]} />)}
        <NewAlbumCard albums={albums} setAlbums={setAlbums} />
      </div> : <div></div>}
  </>
}

function ProfileCard({ user, setUser }) {
  const numberOfAvatars = 7;
  const [avatarIndex, setAvatarIndex] = useState(user['avatar'] || get_new_random_avatar());

  function get_new_random_avatar() {
    return `${Math.random() < 0.5 ? 'm' : 'f'}${Math.floor(Math.random() * numberOfAvatars)}`;
  }

  function assign_new_avatar(new_avatar_name) {
    setAvatarIndex(new_avatar_name);
    axios.put(`${baseUrl}/api/changeAvatar/${user['username']}`, { 'avatar': new_avatar_name })
  }

  return <div className={`${styles.card} ${styles.card_small}`}>
    <div className={styles.card_body}>
      <div className={styles.avatar_section}>
        {avatarIndex && <div>
          <Image src={`/images/characters/${avatarIndex}.png`} alt="Avatar" width={120} height={120} />
        </div>}
        <div className={styles.nav_action} onClick={() => assign_new_avatar(get_new_random_avatar())}>
          <Image src={`/images/reset.png`} alt="Reset" width={40} height={40} />
        </div>
      </div>
      <div>
        <h2>{user['username'] || 'Anonimus'}</h2>
      </div>
      <div>
        <h5>{`${user['name'] || ''} ${user['surname'] || ''}`}</h5>
      </div>
    </div>
  </div>
}

function UploadDocumentCard() {
  const [fileDragging, setFileDragging] = useState(false);
  const [fileToUpload, setFileToUpload] = useState(null);
  const descriptionRef = useRef(null);
  const tagsRef = useRef(null);

  function uploadFile() {
    if (!fileToUpload) {
      alert("First upload file to transfer");
      return;
    }

    const reader = new FileReader();
    reader.addEventListener('load', (event) => {
      const content = event.target.result;
      sendFile(content);
    });
    reader.readAsDataURL(fileToUpload);
  }

  async function sendFile(fileContent) {
    const fileData = { 'fileContent': fileContent, 'fileName': fileToUpload['name'], 'fileType': fileToUpload['type'], 'fileSize': fileToUpload['size'], 'fileCreated': new Date().toISOString(), 'fileLastModefied': new Date(fileToUpload['lastModified']).toISOString(), 'description': descriptionRef.current.value, 'tags': tagsRef.current.value ? tagsRef.current.value.split(',') : [], 'owner': user['username'], 'haveAccsess': [user['username']] };
    descriptionRef.current.value = '';
    tagsRef.current.value = '';
    setFileToUpload(null);
    const response = await axios.post(`${baseUrl}/api/upload`, fileData);
    console.log(response);
  }

  function handleDragOver(event) {
    event.stopPropagation();
    event.preventDefault();
    event.dataTransfer.dropEffect = 'copy';
    setFileDragging(true);
  }

  function handleDragLeaveCapture() {
    setFileDragging(false);
  }

  function handleDrop(event) {
    event.stopPropagation();
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    setFileToUpload(file);
    setFileDragging(false);
  }

  return <div className={`${styles.card} ${styles.card_large}`}>
    <div className={styles.card_nav}>
      <h3>Upload</h3>
      <Image className={styles.nav_action} src='/images/upload.png' alt="Upload" width={40} height={40} onClick={uploadFile} />
    </div>

    <div className={`${styles.card_body} ${fileDragging && styles.no_padding}`} onDragOver={handleDragOver} onDrop={handleDrop} onDragLeaveCapture={handleDragLeaveCapture}>

      {(!fileDragging && !fileToUpload) && <div>
        <input type="file" id="file-selector" name="file-selector" hidden onChange={(e) => setFileToUpload(e.currentTarget.files[0])} />
        <div className={styles.add_file_btn}>
          <label htmlFor="file-selector">+</label>
        </div>
      </div>}

      {(fileDragging) && <div className={`${styles.drop_area}`}>
        <p>Drag file here...</p>
      </div>}

      {(fileToUpload && !fileDragging) && <div className={`${styles.file_preview}`}>

        <div className={styles.uploaded_file_info}>
          <Image src={`/images/${getFileType(fileToUpload)}.png`} alt="File Preview" width={160} height={160} />
          <p>{fileToUpload['name']}</p>
        </div>

        <div>
          <h4><label htmlFor="tags">{`Tags (comma-separated):`}</label></h4>
          <input ref={tagsRef} type="text" id='tags' name="tags" />

          <h4><label htmlFor="comment">Comment:</label></h4>
          <textarea ref={descriptionRef} rows="4" name="comment" />
        </div>

      </div>}
    </div>
  </div>
}

function NewAlbumCard({ albums, setAlbums }) {
  const [albumName, setAlbumName] = useState('');

  function createNewAlbum() {
    if (albumName == '') {
      alert("Enter album name first");
      return;
    }
    axios.post(`${baseUrl}/api/newAlbum`, { 'albumName': albumName }).then(response => setAlbums({ ...albums, albumName: [] }))
  }

  return <div className={`${styles.card} ${styles.card_small}`}>
    <div className={styles.card_nav}>
      <h3>New album</h3>
      <Image className={styles.nav_action} src='/images/add-folder.png' alt="Upload" width={40} height={40} onClick={createNewAlbum} />
    </div>
    <div className={`${styles.card_body}`}>
      <p className={styles.additionalTitle}>Create new empty album</p>
      <form onSubmit={createNewAlbum}>
        <label htmlFor="albumName">Album name</label>
        <input type="text" name="albumName" id="albumName" onChange={(e) => setAlbumName(e.currentTarget.value)} />
        <input type="submit" value='Create' />
      </form>
    </div>
  </div>
}

function getFileType(file) {
  if (file.type.startsWith('image /')) return 'image';
  if (file.type.startsWith('video/')) return 'video';
  if (file.type.startsWith('application/')) return 'document';
  return 'other';
}

function AlbumCard() {
  const [preview, setPreview] = useState(false)
  const [selectedDoc, setSelectedDoc] = useState(null)
  const [documents, setDocuments] = useState([{ 'lastModified': '20.05.2023.', 'name': 'Ime dokumenta', 'tags': '#tag1;#tag2', 'comment': 'Neki koment' }, { 'lastModified': '20.05.2023.', 'name': 'Ime dokumenta', 'tags': '#tag1;#tag2', 'comment': 'Neki koment' }, { 'lastModified': '20.05.2023.', 'name': 'Ime dokumenta', 'tags': '#tag1;#tag2', 'comment': 'Neki koment' }, { 'lastModified': '20.05.2023.', 'name': 'Ime dokumenta', 'tags': '#tag1;#tag2', 'comment': 'Neki koment' }, { 'lastModified': '20.05.2023.', 'name': 'Ime dokumenta', 'tags': '#tag1;#tag2', 'comment': 'Neki koment' }, { 'lastModified': '20.05.2023.', 'name': 'Ime dokumenta', 'tags': '#tag1;#tag2', 'comment': 'Neki koment' }])

  function showPreview(index) {
    setPreview(true);
    setSelectedDoc(index);
  }

  return <div className={`${styles.card} ${styles.card_extra_large}`}>
    <div className={styles.card_nav}>
      <h3>Main album</h3>
    </div>
    {preview ? <DocumentPreview setPreview={setPreview} index={selectedDoc} setDocuments={setDocuments} documents={documents} /> :
      <div className={styles.grid_album}>
        {documents.map((doc, index) => <AlbumDocument doc={doc} showPreview={showPreview} index={index} key={index} />)}

      </div>}
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
