import {useEffect} from 'react';
import useBaseUrl from '@docusaurus/useBaseUrl';

const legacyAnchors = {
  '#timeout': 'action-script-options',
  '#tts-audio-generation-timeout': 'action-script-options',
  '#default-playback-scripts': 'action-script-options',
  '#pre_script': 'action-script-options',
  '#post_script': 'action-script-options',
  '#default-tts-platform': 'tts-defaults-fallback',
  '#default-language': 'tts-defaults-fallback',
  '#default-voice': 'tts-defaults-fallback',
  '#default-dialect': 'tts-defaults-fallback',
  '#fallback-tts-platform': 'tts-defaults-fallback',
  '#default-offset': 'playback-options',
  '#default-start-chime': 'playback-options',
  '#default-end-chime': 'playback-options',
  '#default-crossfade': 'playback-options',
  '#fade-transition': 'playback-options',
  '#delay-before-removing-temporary-files': 'playback-options',
  '#mp3-cover-art': 'playback-options',
  '#custom-chimes-folder': 'chimes',
  '#downloaded-chimes-folder': 'chimes',
  '#temporary-mp3-folder': 'audio-files-folders',
  '#chime_ttssay_url-folder': 'audio-files-folders',
};

export default function LegacyConfigurationRedirect() {
  const configurationPath = useBaseUrl('/docs/documentation/configuration');
  const chimesPath = useBaseUrl('/docs/documentation/chimes');

  useEffect(() => {
    const destination = legacyAnchors[window.location.hash];
    if (destination) {
      const destinationPath = destination === 'chimes'
        ? chimesPath
        : `${configurationPath}/${destination}`;
      window.location.replace(`${destinationPath}${window.location.hash}`);
    }
  }, [chimesPath, configurationPath]);

  return null;
}
