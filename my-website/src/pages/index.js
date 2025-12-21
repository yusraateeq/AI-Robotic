import Link from '@docusaurus/Link';
import Layout from '@theme/Layout';
import styles from './index.module.css';

export default function Home() {
  return (
    <Layout title="AI Native" description="Learn AI through a modern book-style website">
      <main className={styles.hero}>
        <div className={styles.left}>
          <img
            src="https://image2url.com/images/1765046433726-55106d08-040d-4059-a8a8-a4ccba4f7106.jpg"
            alt="Neon AI book and brain illustration"
            className={styles.heroImage}
          />
        </div>

        <div className={styles.right}>
          <div className={styles.badge}>
            AI-NATIVE BOOK SERIES
          </div>

          <h1 className={styles.title}>
            AI & Humanoid <span className={styles.gradient}> Robotics</span>
          </h1>

          <p className={styles.subtitle}>
            A modern, animated book-style learning experience where knowledge meets creativity.
          </p>

          <div className={styles.glassCard}>
            <p>✨ 100% Free Book</p>
            <p>📘 Beginner Friendly</p>
            <p>🤖 AI-Powered Explanations</p>
          </div>

          <div className={styles.buttons}>
            <Link className={styles.primaryButton} to="docs/Module 1/ros2_module1_chapter1">
              Start Reading →
            </Link>
            <Link className={styles.secondaryButton} to="docs/Module 1/ros2_module1_chapter1">
              Explore Chapters 🚀
            </Link>
          </div>
        </div>
      </main>


      {/* -------------------- MIND-BLOWING HIGHLIGHTS -------------------- */}
      <section className={styles.wowSection}>
        <div className={styles.wowContainer}>
          <div className={styles.wowIntro}>
            <h2 className={styles.sectionTitle}>Why This AI Book Will Blow Your Mind</h2>
            <p className={styles.wowSubtitle}>Interactive examples, real robotics case studies, and AI explanations designed to make complex ideas instantly clear.</p>
          </div>

          <div className={styles.wowGrid}>
            <div className={styles.wowCard}>
              <div className={styles.wowIcon} aria-hidden>🤯</div>
              <h3>Concepts Demystified</h3>
              <p>From control loops to perception — learn with visual walkthroughs and live demos that make intuition stick.</p>
              <div className={styles.statBadge}>Instant Understanding</div>
            </div>

            <div className={styles.wowCard}>
              <div className={styles.wowIcon} aria-hidden>⚙️</div>
              <h3>Hands-on Robotics</h3>
              <p>Practical projects and code you can run — mapping theory to real robot behaviour and systems.</p>
              <div className={styles.statBadge}>Run & Experiment</div>
            </div>

            <div className={styles.wowCard}>
              <div className={styles.wowIcon} aria-hidden>💡</div>
              <h3>AI That Explains</h3>
              <p>Context-aware explanations and step-by-step breakdowns so you never feel lost while learning.</p>
              <div className={styles.statBadge}>AI-Powered Help</div>
            </div>
          </div>
        </div>
      </section>




    </Layout>
  );
}


