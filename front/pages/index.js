import styles from "@/styles/Home.module.css"
import { useEffect, useRef, useState } from "react"
import Image from "next/image";
import axios from "axios";
import { baseUrl } from "./_app";

var user = {}

export default function Home() {

  useEffect(() => {
    user = JSON.parse(localStorage.getItem('user')) || {};
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
  const [avatarIndex, setAvatarIndex] = useState(null);

  useEffect(() => {
    setAvatarIndex(user && user['avatar'] ? user['avatar'] : get_new_random_avatar());
  }, [user]);

  function get_new_random_avatar() {
    return `${Math.random() < 0.5 ? 'm' : 'f'}${Math.floor(Math.random() * numberOfAvatars)}`;
  }

  function assign_new_avatar(new_avatar_name) {
    user['avatar'] = new_avatar_name;
    localStorage.setItem('user', JSON.stringify(user));
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
        <h4>{user['email'] || ''}</h4>
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
    const file = event.dataTransfer.files[0]
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
        <input type="file" id="file-selector" name="file-selector" hidden />
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

function getFileType(file) {
  if (file.type.startsWith('image/')) return 'image';
  if (file.type.startsWith('video/')) return 'video';
  if (file.type.startsWith('application/')) return 'document';
  return 'other';
}