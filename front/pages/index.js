import styles from "@/styles/Home.module.css"
import { useEffect, useRef, useState } from "react"
import Image from "next/image";
import axios from "axios";
import { baseUrl } from "./_app";
import { getUserEmail } from "@/helper/helper";


export default function Home() {
  return <>
    <Grid />
  </>
}

function Grid() {
  const [user, setUser] = useState(null);
  const [albums, setAlbums] = useState(null);
  useEffect(() => {
    axios.get(`${baseUrl}/api/user`).then(response => { setUser(response.data); setAlbums(response.data['albums']); }).catch();
  }, []);
  return <>
    {user ?
      <div className={styles.grid}>
        <ProfileCard user={user} setUser={setUser} />
        <UploadDocumentCard user={user} albums={albums} setAlbums={setAlbums} />
        {Object.keys(albums).map(albumName => <AlbumCard key={albumName} albumName={albumName} album={albums[albumName]} albums={albums} setAlbums={setAlbums} user={user} />)}
        <NewAlbumCard albums={albums} setAlbums={setAlbums} />
      </div> : <div></div>}
  </>
}

function ProfileCard({ user, setUser }) {
  const numberOfAvatars = 7;
  const [avatarIndex, setAvatarIndex] = useState(user['avatar'] || get_new_random_avatar());
  const [familyMember, setFamilyMember] = useState('')

  function get_new_random_avatar() {
    return `${Math.random() < 0.5 ? 'm' : 'f'}${Math.floor(Math.random() * numberOfAvatars)}`;
  }

  function assign_new_avatar(new_avatar_name) {
    axios.put(`${baseUrl}/api/changeAvatar/${user['username']}`, { 'avatar': new_avatar_name }).then(response => setAvatarIndex(new_avatar_name)).catch(err => alert("Avatar could not be changed. Try again later."));
  }

  function inviteFamilyMember() {
    axios.post(`${baseUrl}/api/familyInvite`, { 'inviter': getUserEmail(), 'family_member': familyMember }).then(response => handleInvitation(response)).catch(err => alert("Family member could not be invited. Try again later."))
  }

  function handleInvitation(response) {
    alert("Succesfully invited family member!")
    setFamilyMember('')
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
      <div className={styles.shareAlbum}>
        <input type="text" name="inviteFamily" placeholder="Invite family member" value={familyMember} onChange={e => setFamilyMember(e.target.value)} />
        <button className={styles.submitDiv} onClick={inviteFamilyMember}>Invite</button>
      </div>
    </div>
  </div>
}

function UploadDocumentCard({ user, albums, setAlbums }) {
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
    reader.addEventListener('load', async (event) => {
      const content = event.target.result;
      await sendFile(content);
    });
    reader.readAsDataURL(fileToUpload);
  }

  async function sendFile(fileContent) {
    const fileData = { 'fileContent': fileContent, 'fileName': fileToUpload['name'], 'fileType': fileToUpload['type'], 'fileSize': fileToUpload['size'], 'fileCreated': new Date().toISOString(), 'fileLastModefied': new Date(fileToUpload['lastModified']).toISOString(), 'description': descriptionRef.current.value, 'tags': tagsRef.current.value ? tagsRef.current.value.split(',') : [], 'owner': user['username'], 'haveAccsess': [user['username']] };
    descriptionRef.current.value = '';
    tagsRef.current.value = '';
    setFileToUpload(null);
    const response = await axios.post(`${baseUrl}/api/upload`, fileData);
    if (response.status == 200) {
      alert("File uploaded successfully")
      let newAlbums = JSON.parse(JSON.stringify(albums));
      newAlbums['Main Album'].push(response.data);
      setAlbums(newAlbums);
    }
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

  function createNewAlbum(e) {
    e.preventDefault();
    if (albumName == '') {
      alert("Enter album name first");
      return;
    }
    axios.post(`${baseUrl}/api/album`, { 'albumName': albumName }).then(response => { setAlbums({ ...albums, [albumName]: [] }); setAlbumName(''); }).catch(err => alert("Album with that name already exists"));
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
        <input type="text" name="albumName" id="albumName" value={albumName} onChange={(e) => setAlbumName(e.currentTarget.value)} />
        <input className="actionBtn" type="submit" value='Create' />
      </form>
    </div>
  </div>
}

function getFileType(file) {
  if (file.type.startsWith('image/')) return 'image';
  if (file.type.startsWith('video/')) return 'video';
  if (file.type.startsWith('application/')) return 'document';
  return 'other';
}

function AlbumCard({ albumName, album, albums, setAlbums, user }) {
  const [preview, setPreview] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [albumContent, setAlbumContent] = useState(album);
  const [shareAlbumWith, setShareAlbumWith] = useState("");

  function showPreview(index) {
    setPreview(true);
    setSelectedDoc(index);
  }

  function deleteAlbum() {
    let newAlbums = JSON.parse(JSON.stringify(albums));
    delete newAlbums[albumName];
    setAlbums(newAlbums);

    axios.delete(`${baseUrl}/api/album/${albumName}`).then(response => alert("Album deleted sucessfully")).catch(err => alert("Service not available at this moment. Try again later."));
  }

  function uploadAdditionalFile(e) {
    const file = e.target.files[0];
    const reader = new FileReader();
    reader.addEventListener('load', async (event) => {
      const content = event.target.result;
      await sendFileAdditional(content, file);
    });
    reader.readAsDataURL(file);
  }

  async function sendFileAdditional(fileContent, file) {
    const fileData = { 'fileContent': fileContent, 'fileName': file['name'], 'fileType': file['type'], 'fileSize': file['size'], 'fileCreated': new Date().toISOString(), 'fileLastModefied': new Date(file['lastModified']).toISOString(), 'description': "", 'tags': [], 'owner': user['username'], 'haveAccsess': [user['username']] };
    const response = await axios.post(`${baseUrl}/api/upload?albumName=${albumName}`, fileData);
    if (response.status == 200) {
      alert(`File uploaded successfully to ${albumName}`);
    }
  }

  function shareAlbum() {
    if (shareAlbumWith.trim() != "") {
      axios.post(`${baseUrl}/api/shareAlbum`, { 'albumName': albumName, 'shareWith': shareAlbumWith }).then(response => alert("Album shared")).catch(err => console.log("Error while sharing"));
    }
  }

  return <div className={`${styles.card} ${styles.card_extra_large}`}>
    <div className={styles.card_nav}>
      <h3>{albumName}</h3>
      <div className={styles.shareAlbum}>
        <input type="text" name="shareAlbum" placeholder="Share album with" value={shareAlbumWith} onChange={(e) => setShareAlbumWith(e.currentTarget.value)} />
        <button className={styles.submitDiv} onClick={shareAlbum}>Share</button>
      </div>
      <input type="file" id={`file-selector-additional-${albumName}`} name={`file-selector-additional-${albumName}`} hidden onChange={uploadAdditionalFile} />
      {<label className={styles.nav_action} htmlFor={`file-selector-additional-${albumName}`}><Image src='/images/upload.png' alt="Upload" width={40} height={40} /></label>}
      {albumName != 'Main Album' && <Image className={styles.nav_action_second} src='/images/delete_album.png' alt="Delete" width={40} height={40} onClick={deleteAlbum} />}
    </div>
    {preview ? <DocumentPreview setPreview={setPreview} index={selectedDoc} setAlbum={setAlbumContent} album={albumContent} albums={albums} albumName={albumName} setAlbums={setAlbums} /> :
      <div className={styles.grid_album}>
        {albumContent.map((doc, index) => <AlbumDocument doc={doc} showPreview={showPreview} index={index} key={index} />)}

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
        <h4>{doc['fileName']}</h4>
        {doc['fileType'] && <p>{doc['fileType'].split('/')[1].toUpperCase()}</p>}
      </div>
    </div>
  </div>
}

function DocumentPreview({ index, setPreview, setAlbum, album, albums, albumName, setAlbums }) {
  const [tags, setTags] = useState(album[index]['tags']);
  const [comment, setComment] = useState(album[index]['description']);
  const [withAccess, setWithAccess] = useState(album[index]['haveAccess']);
  const [newAlbumSelected, setNewAlbumSelected] = useState(albumName);
  const [shareUsername, setShareUsername] = useState('');
  const [invalidShareEmail, setInvalidShareEmail] = useState('');

  const [editing, setEditing] = useState(false);

  function saveChanges(event) {
    event.preventDefault();
    const editedFile = {
      'tags': (JSON.stringify(album[index]['tags']) != JSON.stringify(tags.split(',')) ? tags : undefined),
      'description': (album[index]['description'] != comment ? comment : undefined),
    }

    const filteredEditFile = Object.fromEntries(Object.entries(editedFile).filter(([_, v]) => v !== undefined));
    axios.put(`${baseUrl}/api/updateFile`, filteredEditFile, { params: { 'fileName': album[index]['fileName'], 'owner': album[index]['owner'] } }).then(_ => setNewValues()).catch(err => console.log("Error while edit. Try again later."));
  }

  function setNewValues() {
    const updatedDocuments = [...album];
    updatedDocuments[index]['tags'] = tags.split(',');
    updatedDocuments[index]['description'] = comment;
    setAlbum(updatedDocuments);
    setEditing(false);
  }

  function setCurrentValues() {
    setTags(album[index]['tags']);
    setComment(album[index]['description']);
    setEditing(false);
  }


  function handleDelete() {
    axios.delete(`${baseUrl}/api/deleteFile`, { params: { 'fileName': album[index]['fileName'], 'owner': album[index]['owner'] } }).then(response => deleteFile()).catch(err => console.log("Error while deleting. Try again later."));
  }

  function deleteFile() {
    setEditing(false);
    setPreview(false);
  }

  function moveToNewAlbum() {
    if (newAlbumSelected == albumName) return;

    let newAlbums = JSON.parse(JSON.stringify(albums));
    if (albumName != 'Main Album') {
      const filesToKeep = newAlbums[albumName].filter(file => file['fileName'] != album[index]['fileName']);
      newAlbums[albumName] = filesToKeep;
      setAlbum(filesToKeep);
    }

    newAlbums[newAlbumSelected].push(album[index]);
    setAlbums(newAlbums);

    axios.put(`${baseUrl}/api/move`, { 'oldAlbum': albumName, 'newAlbum': newAlbumSelected, 'fileName': `${album[index]['owner']},${album[index]['fileName']}` }).then(response => setPreview(false)).catch(err => "Can't move file. Try again later.");
  }

  function downloadDocument() {
    axios.get(`${baseUrl}/api/download`, { params: { 'fileName': album[index]['fileName'], 'owner': album[index]['owner'] } }).then(response => handleDownload(response.data['content'])).catch(err => 'File is not available at this moment. Try again later.');
  }

  function handleDownload(data) {
    const fileData = Buffer.from(data, 'base64');
    const fileBlob = new Blob([fileData], { type: album[index]['fileType'] });
    const fileURL = URL.createObjectURL(fileBlob);

    const link = document.createElement('a');
    link.href = fileURL;
    link.download = `${album[index]['fileName']}`;
    document.body.appendChild(link);
    link.click();
  }

  function shareFile() {
    if (shareUsername == '') return;
    axios.put(`${baseUrl}/api/shareFile`, { 'fileName': album[index]['fileName'], 'shareWith': shareUsername }).then(response => { setWithAccess([...withAccess, shareUsername]); setInvalidShareEmail(false); setShareUsername(''); }).catch(err => setInvalidShareEmail(true));
  }

  return <div className={styles.prev_container}>
    <div className={styles.doc_nav}>
      <div className={styles.back} onClick={() => setPreview(false)}>
        <Image src={'/images/left-arrow.png'} width={24} height={24} alt="back" />
      </div>
      <div className={styles.divider}>{album[index]['fileLastModefied'].replace('Z', '').replace('T', ' ')}</div>
      <div className={styles.divider}>
        <div className={styles.icon} onClick={downloadDocument}>
          <Image src={'/images/download.png'} width={30} height={30} alt="doc" />
        </div>
        {album[index]['owner'] == getUserEmail() && <div className={styles.icon} onClick={() => setEditing(true)}>
          <Image src={'/images/edit.png'} width={30} height={30} alt="doc" />
        </div>}
        {album[index]['owner'] == getUserEmail() && <div className={styles.icon} onClick={handleDelete}>
          <Image src={'/images/delete.png'} width={30} height={30} alt="doc" />
        </div>}
      </div>

    </div>
    <div className={styles.doc_body}>
      <div className={styles.doc_prev}>
        <Image src={'/images/document.png'} width={250} height={250} alt="doc" ></Image>
      </div>
      <div className={styles.doc_details}>
        <div className={styles.topDetails}>
          <div className={styles.details}>
            <h4>Name:</h4>
            <p>{album[index]['fileName']}</p>
          </div>
          <div className={styles.details}>
            <h4>{editing ? <label htmlFor="tags">{`Tags (comma-separated):`}</label> : 'Tags:'}</h4>
            {editing ? <input type="text" id='tags' name="tags" value={tags} onChange={e => setTags(e.target.value)} /> : album[index]['tags'].length > 0 ? <p>{`#${album[index]['tags'].join(" #")}`}</p> : <p></p>}
          </div>
          <div className={styles.details}>
            <h4>{editing ? <label htmlFor="comment">Comment:</label> : 'Comment:'}</h4>
            {editing ? <textarea rows="4" name="comment" value={comment} onChange={e => setComment(e.target.value)} /> : <p>{album[index]['description']}</p>}
          </div>
          <div className={styles.details}>
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
        <div className={styles.bottomDetails}>
          <div className={styles.details}>
            <h4>Move to album</h4>
            <select defaultValue={newAlbumSelected} onChange={e => setNewAlbumSelected(e.target.value)}>
              {Object.keys(albums).map(albumName => <option key={albumName} value={albumName}>{albumName}</option>)}
            </select>
          </div>
          <button className={styles.submitBtn} onClick={moveToNewAlbum}>Move</button>
        </div>
        {album[index]['owner'] == getUserEmail() && <div className={styles.bottomDetails}>
          <div className={styles.details}>
            <h4>{`Share with (username)`}</h4>
            <input type="text" id='share' name="share" value={shareUsername} onChange={e => setShareUsername(e.target.value)} />
          </div>
          <button className={styles.submitBtn} onClick={shareFile}>Share</button>
          {invalidShareEmail && <p className="err">User with that username does not exist</p>}
        </div>}
        {album[index]['owner'] == getUserEmail() && <div className={styles.bottomDetails}>
          <h4>People with access</h4>
          {withAccess.map(personUsername => <AccessItem key={personUsername} personUsername={personUsername} fileAccess={album[index]['fileName']} withAccess={withAccess} setWithAccess={setWithAccess} />)}
        </div>}
      </div>
    </div>
  </div>
}

function AccessItem({ personUsername, fileAccess, withAccess, setWithAccess }) {
  function removeAccess() {
    axios.put(`${baseUrl}/api/removeAccess`, { 'fileWithAccess': fileAccess, 'removeAccessTo': personUsername })
      .then(response => setWithAccess(withAccess.filter(person => person != personUsername)))
      .catch(err => alert("Can't remove your own access. Try again later."));
  }

  return <div className={styles.accessItem}>
    <p>{personUsername}</p>
    {personUsername != getUserEmail() && <div onClick={removeAccess}><Image src='/images/close.png' alt="X" width={20} height={20} /></div>}
  </div>
}
