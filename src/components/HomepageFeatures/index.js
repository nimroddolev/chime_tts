import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';
import useBaseUrl from '@docusaurus/useBaseUrl';

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className={clsx('row', 'row1')} id={styles.hide_overflow}>

          <div className={clsx('col col--4')}>
            <div className={styles.mergeContainer}>
              <div className={styles.cell}>
                <div className={styles.soundContainer}>
                  <div className="text--center">
                    <div className={styles.wave}>
                      <div className={styles.chime}>
                        <img src={useBaseUrl('/img/animations/audio_chime.png')} />
                        <p><font color="00a6e3">Chime</font><br/>media_player.play_media</p>
                      </div>
                      <div className={styles.spacer}>
                        <img src={useBaseUrl('/img/animations/spacer.png')} />
                        <p>chime_tts.say</p>
                      </div>
                      <div className={styles.tts}>
                        <img src={useBaseUrl('/img/animations/audio_tts.png')} className={styles.tts} />
                        <p><font color="ff7100">TTS</font><br/>tts.speak <i>or</i> tts.*_say</p>
                      </div>
                    </div>
                  </div>
                </div>
                <div className={styles.lagText}>
                  <div className="text--center padding-horiz--md">
                    <Heading as="h3">No More Lag</Heading>
                    <p>Locally combine chimes and TTS audio for lag-free playback in a single action call.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className={clsx('col col--4')}>
            <div className={styles.cell}>
              <div className="text--center">
                <div className={styles.puzzleContainer}>
                  <img src={useBaseUrl('/img/animations/tts_puzzle/puzzle1.png')} className={styles.puzzlePiece} />
                  <img src={useBaseUrl('/img/animations/tts_puzzle/puzzle2.png')} className={styles.puzzlePiece} />
                  <img src={useBaseUrl('/img/animations/tts_puzzle/puzzle3.png')} className={styles.puzzlePiece} />
                  <img src={useBaseUrl('/img/animations/tts_puzzle/puzzle4.png')} className={styles.puzzlePiece} />
                  <img src={useBaseUrl('/img/animations/tts_puzzle/puzzle5.png')} className={styles.puzzlePiece} />
                  <img src={useBaseUrl('/img/animations/tts_puzzle/puzzle6.png')} className={styles.puzzlePiece} />
                  <img src={useBaseUrl('/img/animations/tts_puzzle/puzzle7.png')} className={styles.puzzlePiece} />
                  <img src={useBaseUrl('/img/animations/tts_puzzle/puzzle8.png')} className={styles.puzzlePiece} />
                  <img src={useBaseUrl('/img/animations/tts_puzzle/puzzle9.png')} className={styles.puzzlePiece} />
                </div>
              </div>
              <div className="text--center padding-horiz--md">
                <Heading as="h3">Customizable</Heading>
                <p>Create fully personalized notifications with a mix of TTS platforms, voices and languages.</p>
              </div>
            </div>
          </div>

          <div className={clsx('col col--4')}>
            <div className={styles.cell}>
              <div className="text--center padding-horiz--md">
                <div className={styles.knifeDiv}>
                  <div className={styles.bodyDiv}>
                    <img src={useBaseUrl('/img/animations/knife/body.png')} className={styles.knifeBody} />
                    <img src={useBaseUrl('/img/animations/knife/speed.png')} className={styles.knifeSpeed} />
                    <img src={useBaseUrl('/img/animations/knife/pitch.png')} className={styles.knifePitch} />
                    <img src={useBaseUrl('/img/animations/knife/chimes.png')} className={styles.knifeChimes} />
                    <img src={useBaseUrl('/img/animations/knife/tts_platform.png')} className={styles.knifeTtsPlatform} />
                    <img src={useBaseUrl('/img/animations/knife/offset.png')} className={styles.knifeOffset} />
                  </div>
                </div>
                <Heading as="h3">Fine Tuning</Heading>
                <p>Easily adjustment your TTS audio with a suite of tools and a simple user-interface.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section >
  );
}
