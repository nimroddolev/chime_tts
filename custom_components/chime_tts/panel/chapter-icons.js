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
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path d="M9 18V6l10-2v12" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M9 9l10-2" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
      <circle cx="6" cy="18" r="3" fill="currentColor"/>
      <circle cx="16" cy="16" r="3" fill="currentColor"/>
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
