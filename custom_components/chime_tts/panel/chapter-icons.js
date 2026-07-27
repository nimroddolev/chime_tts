// Shared chapter-title SVGs. Keeping them together makes it easy to keep the
// top-level areas visually consistent without adding separate asset requests.
export const CHAPTER_ICONS = {
  configuration: `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path d="M4 7h16M4 17h16M8 4v6M16 14v6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
      <circle cx="8" cy="7" r="2" fill="currentColor"/>
      <circle cx="16" cy="17" r="2" fill="currentColor"/>
    </svg>
  `,
  chime_sets: `
    <svg viewBox="0 0 150 150" fill="currentColor" aria-hidden="true" focusable="false" style="fill-rule:evenodd;clip-rule:evenodd;stroke-linejoin:round">
      <g transform="matrix(6.25,0,0,6.25,0,-1)"><path d="M12,2.3L20.2,6.55L12,10.9L3.8,6.55L12,2.3Z" fill-opacity=".34"/></g>
      <g transform="matrix(6.25,0,0,6.25,-1,1)"><path d="M3.8,6.55L12,10.9L12,21.1L3.8,16.8L3.8,6.55Z" fill-opacity=".16"/></g>
      <g transform="matrix(6.25,0,0,6.25,1,1)"><path d="M12,10.9L20.2,6.55L20.2,16.8L12,21.1L12,10.9Z" fill-opacity=".25"/></g>
      <g transform="matrix(6.914894,0,0,6.914894,-7.978723,-7.779255)"><path d="M12,2.3L20.2,6.55L12,10.9L3.8,6.55L12,2.3ZM3.8,6.55L12,10.9L12,21.1L3.8,16.8L3.8,6.55ZM20.2,6.55L12,10.9L12,21.1L20.2,16.8L20.2,6.55Z" fill="none" stroke="currentColor" stroke-width="1.37"/></g>
      <g transform="matrix(6.25,0,0,6.25,-6.25,12.5)">
        <g transform="matrix(1,0,0,1.023969,0,-2.409279)"><path d="M8,11.1C8,11.1 8,15.208 8,15.212C8,16.227 6.628,14.409 6.85,14.5L6.85,9.775L11.2,12L11.2,16.35C10.2,18.354 9.828,15.559 10.05,15.65L10.05,12.77L8,11.707L8,11.1Z"/></g>
        <g transform="matrix(1.359693,-.494888,.34202,.939693,-2.858075,-4.359272)"><circle cx="2" cy="20" r="1"/></g>
        <g transform="matrix(1.409539,-.51303,.34202,.939693,.092078,-3.34113)"><circle cx="2" cy="20" r="1"/></g>
      </g>
      <g transform="matrix(6.155048,-1.085301,1.085301,6.155048,32.815003,8.941252)">
        <path d="M12.685,12.044L11.994,12.869C11.994,12.869 11.237,12.508 11.144,12.315C11.077,12.174 11.2,16.35 11.2,16.35C10.2,18.354 9.828,15.559 10.05,15.65L10.05,12.77L10.184,10.714L12.685,12.044Z" transform="translate(-1)"/>
        <g transform="matrix(1.409539,-.51303,.34202,.939693,-.907922,-1.34113)"><circle cx="2" cy="20" r="1"/></g>
      </g>
      <g transform="matrix(3.053384,-3.919841,3.463766,2.698122,-2.177338,35.058841)">
        <path d="M12.4,12.34L11.763,13.018C11.763,13.018 10.902,12.525 11.006,12.46C11.062,12.424 11.2,16.35 11.2,16.35C10.2,18.354 9.828,15.559 10.05,15.65L10.05,12.77L10.184,10.714L12.4,12.34Z" transform="translate(-1)"/>
        <g transform="matrix(1.409539,-.51303,.34202,.939693,-.907922,-1.34113)"><circle cx="2" cy="20" r="1"/></g>
      </g>
    </svg>
  `,
  notify_profiles: `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path d="M18 10a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 22h4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  `,
  logs: `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <rect x="5" y="3" width="14" height="18" rx="2" fill="none" stroke="currentColor" stroke-width="1.8"/>
      <path d="M9 8h6M9 12h6M9 16h4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
    </svg>
  `,
  about: `
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.8"/>
      <path d="M12 11v6M12 7.5v.1" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    </svg>
  `,
};
