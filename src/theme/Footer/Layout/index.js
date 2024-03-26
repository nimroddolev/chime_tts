import React from 'react';
import clsx from 'clsx';
import './styles.css'

export default function FooterLayout({ style, links, logo, copyright }) {
  return (
    <footer
      className={clsx('footer', {
        'footer--dark': style === 'dark',
      })}>
      <div className="container container-fluid">
        {links}
        {(logo || copyright) && (
          <div className="footer__bottom text--center">
            {logo && <div className="margin-bottom--sm">{logo}</div>}
            <p>If you find Chime TTS useful, please consider showing your support: <a href="https://www.buymeacoffee.com/nimroddolev" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy me a coffee" id="buyMeACoffee" /></a></p>
            {copyright}
          </div>
        )}
      </div>
    </footer>
  );
}
