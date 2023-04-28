import styles from "../styles/PageContainer.module.css"

export default function PageContainer({children}){
return <div className={styles.pageStyle}>
{children}
</div>
}