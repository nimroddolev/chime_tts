import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';
import useBaseUrl from '@docusaurus/useBaseUrl';

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">

          <div className={styles.mergeContainer}>
            <div className={styles.cell}>
              <div className={styles.soundContainer}>
                <div className="text--center">
                  <div className={styles.chime}>
                    <img src={useBaseUrl('/img/animations/audio_chime.png')} />
                    <p>media_player.play_media</p>
                  </div>
                  <div className={styles.spacer}>
                    <img src={useBaseUrl('/img/animations/spacer.png')} />
                    <p>chime_tts.say</p>
                  </div>
                  <div className={styles.tts}>
                    <img src={useBaseUrl('/img/animations/audio_tts.png')} className={styles.tts} />
                    <p>media_player.play_media</p>
                  </div>
                </div>
              </div>
              <div className="text--center padding-horiz--md">
                <Heading as="h3">No More Lag</Heading>
                <p>Locally combine chimes and TTS audio before playback in a single service call, for lag-free playback.</p>
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
                <p>Mix TTS platforms & chimes together to create fully personalized notifications.</p>
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
                <Heading as="h3">Full Customization</Heading>
                <p>Tweak your audio to create rich notifications with a powerful and clear user-interface.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section >
  );
}
