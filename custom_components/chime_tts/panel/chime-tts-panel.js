const PANEL_TAG = "chime-tts-settings-panel";
const OPTION_ICON_DATA_URLS = {
  "add_cover_art": "data:image/svg+xml;utf8,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%2064%2064%22%20fill=%22none%22%3E%0A%20%20%3Crect%20x=%2214%22%20y=%2216%22%20width=%2222%22%20height=%2222%22%20rx=%226%22%20fill=%22%2303a9f4%22/%3E%0A%20%20%3Ccircle%20cx=%2225%22%20cy=%2227%22%20r=%224%22%20fill=%22%23fff%22/%3E%0A%20%20%3Cpath%20d=%22M42%2022h8M42%2030h10M42%2038h6%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M18%2044c3-3%205-4%207-4s4%201%207%204%22%20stroke=%22%237dd3fc%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%3C/svg%3E",
  "crossfade": "data:image/svg+xml;utf8,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%2064%2064%22%20fill=%22none%22%3E%0A%20%20%3Cpath%20d=%22M16%2042c3-10%206-16%209-16s6%206%209%2016%22%20stroke=%22%2303a9f4%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M30%2042c3-10%206-16%209-16s6%206%209%2016%22%20stroke=%22%237dd3fc%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M28%2023h8%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%3C/svg%3E",
  "custom_chimes_path": "data:image/svg+xml;utf8,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%2064%2064%22%20fill=%22none%22%3E%0A%20%20%3Cpath%20d=%22M12%2021h14l4%204h20v18c0%203-2%205-5%205H17c-3%200-5-2-5-5V21z%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linejoin=%22round%22/%3E%0A%20%20%3Ccircle%20cx=%2222%22%20cy=%2238%22%20r=%223.5%22%20fill=%22%23f472b6%22/%3E%0A%20%20%3Crect%20x=%2228%22%20y=%2234%22%20width=%228%22%20height=%228%22%20rx=%222.5%22%20fill=%22%2303a9f4%22/%3E%0A%20%20%3Cpath%20d=%22M44%2035l3%206h-6l3-6z%22%20fill=%22%23facc15%22/%3E%0A%20%20%3Cpath%20d=%22M38%2018l1.2%202.6%202.8.4-2%201.9.5%202.8-2.5-1.4-2.5%201.4.5-2.8-2-1.9%202.8-.4L38%2018z%22%20fill=%22%2322c55e%22/%3E%0A%3C/svg%3E",
  "default_language_key": "data:image/svg+xml;utf8,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%2064%2064%22%20fill=%22none%22%3E%0A%20%20%3Cpath%20d=%22M21%2020h10M26%2020v24M16%2031h20%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M37%2039c3-2%205-5%206-9%201%204%203%207%206%209%22%20stroke=%22%2303a9f4%22%20stroke-width=%223%22%20stroke-linecap=%22round%22%20stroke-linejoin=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M41%2045h12%22%20stroke=%22%237dd3fc%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%3C/svg%3E",
  "default_tld_key": "data:image/svg+xml;utf8,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%2064%2064%22%20fill=%22none%22%3E%0A%20%20%3Ccircle%20cx=%2226%22%20cy=%2232%22%20r=%2212%22%20stroke=%22%2303a9f4%22%20stroke-width=%223%22/%3E%0A%20%20%3Cpath%20d=%22M14%2032h24M26%2020c-3%204-4%208-4%2012s1%208%204%2012M26%2020c3%204%204%208%204%2012s-1%208-4%2012%22%20stroke=%22%237dd3fc%22%20stroke-width=%222.5%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M43%2024h9M43%2032h7M43%2040h9%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%3C/svg%3E",
  "default_voice_key": "data:image/svg+xml;utf8,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%2064%2064%22%20fill=%22none%22%3E%0A%20%20%3Crect%20x=%2225%22%20y=%2218%22%20width=%2214%22%20height=%2222%22%20rx=%227%22%20stroke=%22%2303a9f4%22%20stroke-width=%223%22/%3E%0A%20%20%3Cpath%20d=%22M20%2032c0%207%205%2012%2012%2012s12-5%2012-12%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M32%2044v6%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M24%2050h16%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%3C/svg%3E",
  "fade_transition_key": "data:image/svg+xml;utf8,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%2064%2064%22%20fill=%22none%22%3E%0A%20%20%3Cpath%20d=%22M17%2042V22%22%20stroke=%22%237ea6b7%22%20stroke-width=%224%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M26%2042V18%22%20stroke=%22%237dd3fc%22%20stroke-width=%224%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M35%2042V25%22%20stroke=%22%2303a9f4%22%20stroke-width=%224%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M44%2042V31%22%20stroke=%22%23d7edf8%22%20stroke-width=%224%22%20stroke-linecap=%22round%22/%3E%0A%3C/svg%3E",
  "fallback_tts_platform_key": "data:image/svg+xml;utf8,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%2064%2064%22%20fill=%22none%22%3E%0A%20%20%3Crect%20x=%2212%22%20y=%2218%22%20width=%2216%22%20height=%2224%22%20rx=%225%22%20stroke=%22%237ea6b7%22%20stroke-width=%223%22/%3E%0A%20%20%3Cpath%20d=%22M31%2030h9%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M36%2025l5%205-5%205%22%20stroke=%22%2303a9f4%22%20stroke-width=%223%22%20stroke-linecap=%22round%22%20stroke-linejoin=%22round%22/%3E%0A%20%20%3Crect%20x=%2242%22%20y=%2218%22%20width=%2210%22%20height=%2224%22%20rx=%225%22%20fill=%22%2303a9f4%22/%3E%0A%3C/svg%3E",
  "offset": "data:image/svg+xml;utf8,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%2064%2064%22%20fill=%22none%22%3E%0A%20%20%3Cpath%20d=%22M16%2038c3-6%206-12%209%200s6%2012%209%200%206-12%209%200%22%20stroke=%22%2303a9f4%22%20stroke-width=%223%22%20stroke-linecap=%22round%22%20stroke-linejoin=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M16%2024h12%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M25%2020l4%204-4%204%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22%20stroke-linejoin=%22round%22/%3E%0A%3C/svg%3E",
  "queue_timeout": "data:image/svg+xml;utf8,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%2064%2064%22%20fill=%22none%22%3E%0A%20%20%3Ccircle%20cx=%2224%22%20cy=%2231%22%20r=%2210%22%20stroke=%22%2303a9f4%22%20stroke-width=%223%22/%3E%0A%20%20%3Cpath%20d=%22M24%2024v8l5%203%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22%20stroke-linejoin=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M40%2024h10M40%2031h8M40%2038h6%22%20stroke=%22%237ea6b7%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%3C/svg%3E",
  "remove_temp_file_delay": "data:image/svg+xml;utf8,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%2064%2064%22%20fill=%22none%22%3E%0A%20%20%3Cpath%20d=%22M24%2019h16%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M27%2019l1%2023c.1%202%201.4%203%203.3%203h5.4c1.9%200%203.2-1%203.3-3l1-23%22%20stroke=%22%237ea6b7%22%20stroke-width=%223%22%20stroke-linecap=%22round%22%20stroke-linejoin=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M29%2019l1.5-3h9L41%2019%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22%20stroke-linejoin=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M31%2025v13M37%2025v13%22%20stroke=%22%2303a9f4%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Ccircle%20cx=%2246%22%20cy=%2218%22%20r=%227%22%20fill=%22%23f59e0b%22/%3E%0A%20%20%3Cpath%20d=%22M46%2015v3l2%201%22%20stroke=%22%23fff%22%20stroke-width=%222.5%22%20stroke-linecap=%22round%22%20stroke-linejoin=%22round%22/%3E%0A%3C/svg%3E",
  "temp_chimes_path": "data:image/svg+xml;utf8,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%2064%2064%22%20fill=%22none%22%3E%0A%20%20%3Cpath%20d=%22M12%2021h15l4%204h21v18c0%203-2%205-5%205H17c-3%200-5-2-5-5V21z%22%20stroke=%22%2303a9f4%22%20stroke-width=%223%22%20stroke-linejoin=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M32%2029v10%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M27%2035l5%205%205-5%22%20stroke=%22%237dd3fc%22%20stroke-width=%223%22%20stroke-linecap=%22round%22%20stroke-linejoin=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M25%2043h14%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%3C/svg%3E",
  "temp_path": "data:image/svg+xml;utf8,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%2064%2064%22%20fill=%22none%22%3E%0A%20%20%3Cpath%20d=%22M12%2021h15l4%204h21v18c0%203-2%205-5%205H17c-3%200-5-2-5-5V21z%22%20stroke=%22%2303a9f4%22%20stroke-width=%223%22%20stroke-linejoin=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M29%2028h8v5l-2%202%202%202v5h-8v-5l2-2-2-2v-5z%22%20stroke=%22%23d7edf8%22%20stroke-width=%222.8%22%20stroke-linejoin=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M29%2033h8%22%20stroke=%22%237dd3fc%22%20stroke-width=%222.8%22%20stroke-linecap=%22round%22/%3E%0A%3C/svg%3E",
  "tts_platform_key": "data:image/svg+xml;utf8,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%2064%2064%22%20fill=%22none%22%3E%0A%20%20%3Crect%20x=%2212%22%20y=%2218%22%20width=%2218%22%20height=%2228%22%20rx=%226%22%20stroke=%22%2303a9f4%22%20stroke-width=%223%22/%3E%0A%20%20%3Crect%20x=%2235%22%20y=%2218%22%20width=%2218%22%20height=%2210%22%20rx=%225%22%20fill=%22%2303a9f4%22/%3E%0A%20%20%3Crect%20x=%2235%22%20y=%2232%22%20width=%2218%22%20height=%226%22%20rx=%223%22%20fill=%22%237ea6b7%22/%3E%0A%20%20%3Crect%20x=%2235%22%20y=%2242%22%20width=%2214%22%20height=%226%22%20rx=%223%22%20fill=%22%237ea6b7%22/%3E%0A%3C/svg%3E",
  "tts_timeout": "data:image/svg+xml;utf8,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%2064%2064%22%20fill=%22none%22%3E%0A%20%20%3Cpath%20d=%22M17%2024h18%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M26%2024v16%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Cpath%20d=%22M21%2040h10%22%20stroke=%22%23d7edf8%22%20stroke-width=%223%22%20stroke-linecap=%22round%22/%3E%0A%20%20%3Ccircle%20cx=%2244%22%20cy=%2231%22%20r=%2210%22%20stroke=%22%2303a9f4%22%20stroke-width=%223%22/%3E%0A%20%20%3Cpath%20d=%22M44%2026v6l4%203%22%20stroke=%22%237dd3fc%22%20stroke-width=%223%22%20stroke-linecap=%22round%22%20stroke-linejoin=%22round%22/%3E%0A%3C/svg%3E",
  "www_path": "data:image/svg+xml;utf8,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%2064%2064%22%20fill=%22none%22%3E%0A%20%20%3Cpath%20d=%22M12%2021h15l4%204h21v18c0%203-2%205-5%205H17c-3%200-5-2-5-5V21z%22%20stroke=%22%2303a9f4%22%20stroke-width=%223%22%20stroke-linejoin=%22round%22/%3E%0A%20%20%3Ccircle%20cx=%2236%22%20cy=%2238%22%20r=%227%22%20stroke=%22%23d7edf8%22%20stroke-width=%222.6%22/%3E%0A%20%20%3Cpath%20d=%22M29%2038h14M36%2031c-1.6%202-2.4%204.3-2.4%207s.8%205%202.4%207M36%2031c1.6%202%202.4%204.3%202.4%207s-.8%205-2.4%207%22%20stroke=%22%237dd3fc%22%20stroke-width=%222.2%22%20stroke-linecap=%22round%22/%3E%0A%3C/svg%3E",
};

const template = document.createElement("template");
template.innerHTML = `
  <style>
    :host {
      box-sizing: border-box;
      display: block;
      min-height: 100%;
      color: var(--primary-text-color);
    }

    *,
    *::before,
    *::after {
      box-sizing: inherit;
    }

    a {
      color: var(--primary-color);
    }

    .layout {
      max-width: 1180px;
      margin: 0 auto;
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 0;
    }

    .topbar-wrap {
      position: sticky;
      top: 0;
      z-index: 10;
      width: 100%;
      backdrop-filter: blur(14px);
      background: color-mix(in srgb, var(--card-background-color) 72%, transparent);
      border-bottom: 1px solid color-mix(in srgb, var(--divider-color) 86%, transparent);
    }

    .topbar {
      width: 100%;
      margin: 0;
      height: 56px;
      padding: 0 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }

    .topbar-notice {
      padding: 0 24px 12px;
    }

    .topbar-notice-inner {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      min-height: 32px;
      padding: 8px 12px;
      border-radius: 999px;
      border: 1px solid color-mix(in srgb, var(--warning-color, #f59e0b) 36%, transparent);
      background: color-mix(in srgb, var(--warning-color, #f59e0b) 12%, transparent);
      color: var(--primary-text-color);
      font-size: 0.88rem;
      line-height: 1.35;
    }

    .topbar-notice-label {
      font-weight: 700;
      white-space: nowrap;
    }

    .topbar-main {
      display: flex;
      align-items: center;
      min-width: 0;
      margin-left: 10px;
    }

    .topbar-actions {
      display: flex;
      align-items: center;
      gap: 14px;
      flex: 0 0 auto;
    }

    .topbar-text {
      min-width: 0;
    }

    .topbar-title {
      margin: 0;
      font-size: 1.5rem;
      font-weight: 400;
      color: var(--primary-text-color);
      line-height: 1;
      letter-spacing: -0.012em;
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }

    .topbar-version {
      font-size: 0.875rem;
      font-weight: 600;
      line-height: 1;
      color: var(--secondary-text-color);
      letter-spacing: 0;
    }

    .section {
      border: 1px solid var(--divider-color);
      border-radius: 24px;
      background: color-mix(in srgb, var(--card-background-color) 92%, white 8%);
      box-shadow: 0 12px 32px rgba(0, 0, 0, 0.08);
    }

    .section p,
    .hint,
    .message {
      margin: 0;
      color: var(--secondary-text-color);
      line-height: 1.6;
    }

    button {
      appearance: none;
      border: 0;
      border-radius: 999px;
      padding: 12px 18px;
      font: inherit;
      font-weight: 700;
      cursor: pointer;
      transition: transform 120ms ease, opacity 120ms ease, box-shadow 120ms ease;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }

    button:hover {
      transform: translateY(-1px);
    }

    button:disabled {
      cursor: not-allowed;
      transform: none;
      box-shadow: none;
    }

    .button-primary {
      color: var(--text-primary-color, #fff);
      background: linear-gradient(135deg, var(--primary-color), color-mix(in srgb, var(--primary-color) 72%, black 28%));
      box-shadow: 0 16px 28px rgba(3, 169, 244, 0.28);
    }

    .button-secondary {
      color: var(--primary-text-color);
      background: color-mix(in srgb, var(--card-background-color) 88%, white 12%);
      border: 1px solid var(--divider-color);
      box-shadow: none;
    }

    .button-restart {
      color: #fff;
      background: color-mix(in srgb, var(--error-color, #d32f2f) 70%, black 30%);
      border: 1px solid color-mix(in srgb, var(--error-color, #d32f2f) 72%, white 28%);
      box-shadow: 0 0 0 0 color-mix(in srgb, var(--error-color, #d32f2f) 0%, transparent);
      animation: restartPulse 1s ease-in-out infinite;
    }

    .save-slot {
      width: 80px;
      flex: 0 0 80px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }

    .save-slot .button-primary {
      width: 100%;
    }

    .button-primary:disabled {
      background: color-mix(in srgb, var(--disabled-color, #9aa0a6) 78%, black 22%);
      color: color-mix(in srgb, var(--primary-text-color) 88%, transparent);
    }

    .save-status {
      width: 100%;
      height: 40px;
      border-radius: 999px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-size: 1rem;
      font-weight: 700;
      line-height: 1;
      border: 1px solid transparent;
    }

    .save-status.success {
      color: var(--primary-color);
      background: color-mix(in srgb, var(--primary-color) 12%, transparent);
      border-color: color-mix(in srgb, var(--primary-color) 28%, transparent);
    }

    .save-status.error {
      color: var(--error-color, #d32f2f);
      background: color-mix(in srgb, var(--error-color, #d32f2f) 10%, transparent);
      border-color: color-mix(in srgb, var(--error-color, #d32f2f) 24%, transparent);
    }

    .button-spinner {
      width: 16px;
      height: 16px;
      border-radius: 999px;
      border: 2px solid rgba(255, 255, 255, 0.28);
      border-top-color: rgba(255, 255, 255, 0.95);
      animation: buttonSpin 0.8s linear infinite;
    }

    @keyframes restartPulse {
      0%,
      100% {
        border-color: color-mix(in srgb, var(--error-color, #d32f2f) 35%, transparent);
        box-shadow: 0 0 0 0 color-mix(in srgb, var(--error-color, #d32f2f) 0%, transparent);
      }

      50% {
        border-color: color-mix(in srgb, var(--error-color, #d32f2f) 90%, white 10%);
        box-shadow: 0 0 0 2px color-mix(in srgb, var(--error-color, #d32f2f) 28%, transparent);
      }
    }

    @keyframes buttonSpin {
      from {
        transform: rotate(0deg);
      }

      to {
        transform: rotate(360deg);
      }
    }

    .topbar-link {
      color: var(--primary-color);
      font: inherit;
      font-weight: 600;
      text-decoration: none;
      white-space: nowrap;
    }

    .topbar-link:hover {
      text-decoration: underline;
    }

    .message {
      margin-bottom: 18px;
      padding: 16px 18px;
      border-radius: 18px;
      border: 1px solid;
    }

    .message.success {
      border-color: rgba(56, 142, 60, 0.35);
      background: rgba(56, 142, 60, 0.08);
      color: var(--primary-text-color);
    }

    .message.error {
      border-color: rgba(211, 47, 47, 0.35);
      background: rgba(211, 47, 47, 0.08);
      color: var(--primary-text-color);
    }

    form {
      display: flex;
      flex-direction: column;
      gap: 18px;
    }

    .section {
      padding: 22px;
    }

    .section-header {
      margin-bottom: 18px;
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: flex-start;
      flex-wrap: wrap;
    }

    .section-header-copy {
      min-width: 0;
    }

    .section-header-actions {
      display: flex;
      align-items: center;
      gap: 10px;
      flex: 0 0 auto;
    }

    .section-header h2 {
      margin: 0 0 6px;
      font-size: 1.25rem;
      letter-spacing: -0.02em;
    }

    .field-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
    }

    :host([narrow]) .field-grid {
      grid-template-columns: 1fr;
    }

    .field {
      display: flex;
      flex-direction: column;
      gap: 8px;
      padding: 16px;
      border-radius: 18px;
      background: color-mix(in srgb, var(--secondary-background-color) 64%, transparent);
      border: 1px solid transparent;
    }

    .field.wide {
      grid-column: 1 / -1;
    }

    .field.error {
      border-color: rgba(211, 47, 47, 0.45);
      background: rgba(211, 47, 47, 0.05);
    }

    .field.changed {
      border-color: color-mix(in srgb, var(--primary-color) 38%, transparent);
      background: color-mix(in srgb, var(--primary-color) 7%, transparent);
    }

    .field-top {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: flex-start;
    }

    .field-header {
      display: flex;
      gap: 14px;
      align-items: center;
      min-width: 0;
    }

    .field-icon {
      width: 56px;
      height: 56px;
      flex: 0 0 56px;
      display: block;
      object-fit: cover;
    }

    .field-copy {
      min-width: 0;
    }

    .field-label {
      margin: 0;
      font-weight: 700;
      color: var(--primary-text-color);
    }

    .field-changed-pill {
      padding: 2px 8px;
      border-radius: 999px;
      background: color-mix(in srgb, var(--primary-color) 14%, transparent);
      color: var(--primary-color);
      font-size: 0.74rem;
      font-weight: 700;
      letter-spacing: 0.02em;
      text-transform: uppercase;
    }

    .field-label-row {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      min-width: 0;
    }

    .field-help-link {
      width: 22px;
      height: 22px;
      border-radius: 999px;
      border: 1px solid color-mix(in srgb, var(--primary-color) 34%, transparent);
      color: var(--primary-color);
      background: color-mix(in srgb, var(--primary-color) 10%, transparent);
      display: inline-flex;
      align-items: center;
      justify-content: center;
      text-decoration: none;
      font-size: 0.82rem;
      font-weight: 700;
      line-height: 1;
      flex: 0 0 auto;
    }

    .field-help-link:hover {
      background: color-mix(in srgb, var(--primary-color) 16%, transparent);
      text-decoration: none;
    }

    .field-help-link:focus-visible {
      outline: 2px solid color-mix(in srgb, var(--primary-color) 45%, transparent);
      outline-offset: 2px;
    }

    .field-description {
      margin: 4px 0 0;
      font-size: 0.92rem;
      color: var(--secondary-text-color);
    }

    .required {
      font-size: 0.78rem;
      font-weight: 700;
      color: var(--primary-color);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      white-space: nowrap;
    }

    .control,
    .control-select {
      width: 100%;
      border: 1px solid var(--divider-color);
      border-radius: 14px;
      background: var(--card-background-color);
      color: var(--primary-text-color);
      padding: 12px 14px;
      font: inherit;
    }

    .control:focus,
    .control-select:focus {
      outline: 2px solid color-mix(in srgb, var(--primary-color) 45%, transparent);
      outline-offset: 0;
      border-color: var(--primary-color);
    }

    .input-row {
      display: flex;
      gap: 10px;
      align-items: stretch;
    }

    .input-row .control {
      flex: 1 1 auto;
      min-width: 0;
    }

    .browse-button {
      flex: 0 0 auto;
      padding: 12px 16px;
      border-radius: 14px;
      border: 1px solid var(--divider-color);
      background: color-mix(in srgb, var(--card-background-color) 92%, white 8%);
      color: var(--primary-text-color);
      box-shadow: none;
    }

    .browse-button:disabled {
      opacity: 0.7;
    }

    .path-inline-action {
      flex: 0 0 auto;
      padding: 10px 14px;
      min-height: 48px;
      border-radius: 14px;
      border: 1px solid color-mix(in srgb, var(--error-color, #d32f2f) 42%, transparent);
      background: color-mix(in srgb, var(--error-color, #d32f2f) 12%, transparent);
      color: var(--primary-text-color);
      box-shadow: none;
      white-space: nowrap;
    }

    .control-checkbox {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 4px 0;
      font-weight: 600;
      color: var(--primary-text-color);
    }

    .control-checkbox input {
      width: 20px;
      height: 20px;
      accent-color: var(--primary-color);
    }

    .error-text {
      font-size: 0.84rem;
      color: var(--error-color, #d32f2f);
    }

    .error-text:empty {
      display: none;
    }

    .field-note {
      padding: 12px 14px;
      border-radius: 14px;
      font-size: 0.88rem;
      line-height: 1.45;
      border: 1px solid color-mix(in srgb, var(--primary-color) 24%, transparent);
      background: color-mix(in srgb, var(--primary-color) 10%, transparent);
      color: var(--primary-text-color);
    }

    .field-subhint {
      padding: 10px 12px;
      border-radius: 14px;
      font-size: 0.86rem;
      line-height: 1.45;
      border: 1px solid var(--divider-color);
      background: color-mix(in srgb, var(--secondary-background-color) 64%, transparent);
      color: var(--secondary-text-color);
    }

    .field-subhint.info {
      border-color: color-mix(in srgb, var(--primary-color) 24%, transparent);
      background: color-mix(in srgb, var(--primary-color) 10%, transparent);
      color: var(--primary-text-color);
    }

    .field-subhint.success {
      border-color: color-mix(in srgb, var(--success-color, #2e7d32) 26%, transparent);
      background: color-mix(in srgb, var(--success-color, #2e7d32) 10%, transparent);
      color: var(--primary-text-color);
    }

    .field-subhint.error {
      border-color: color-mix(in srgb, var(--error-color, #d32f2f) 26%, transparent);
      background: color-mix(in srgb, var(--error-color, #d32f2f) 8%, transparent);
      color: var(--primary-text-color);
    }

    .field-subhint-links {
      margin-top: 8px;
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }

    .field-subhint-links a {
      color: var(--primary-color);
      text-decoration: none;
      font-weight: 600;
      word-break: break-all;
    }

    .field-subhint-links a:hover {
      text-decoration: underline;
    }

    .footer {
      display: flex;
      justify-content: flex-end;
      align-items: center;
      gap: 16px;
      flex-wrap: wrap;
      padding: 8px 2px 4px;
    }

    .loading {
      padding: 56px 24px;
      text-align: center;
      color: var(--secondary-text-color);
    }

    .picker-overlay {
      position: fixed;
      inset: 0;
      z-index: 30;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px;
      background: rgba(0, 0, 0, 0.45);
      backdrop-filter: blur(6px);
    }

    .picker-dialog {
      width: min(860px, 100%);
      max-height: min(80vh, 760px);
      display: flex;
      flex-direction: column;
      overflow: hidden;
      border-radius: 24px;
      border: 1px solid var(--divider-color);
      background: var(--card-background-color);
      box-shadow: 0 20px 48px rgba(0, 0, 0, 0.28);
    }

    .confirm-overlay {
      position: fixed;
      inset: 0;
      z-index: 40;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px;
      background: rgba(0, 0, 0, 0.45);
      backdrop-filter: blur(6px);
    }

    .confirm-dialog {
      width: min(520px, 100%);
      display: flex;
      flex-direction: column;
      gap: 16px;
      padding: 22px;
      border-radius: 24px;
      border: 1px solid var(--divider-color);
      background: var(--card-background-color);
      box-shadow: 0 20px 48px rgba(0, 0, 0, 0.28);
    }

    .confirm-title {
      margin: 0;
      color: var(--primary-text-color);
      font-size: 1.2rem;
      font-weight: 700;
    }

    .confirm-copy {
      margin: 0;
      color: var(--secondary-text-color);
      line-height: 1.6;
    }

    .confirm-actions {
      display: flex;
      justify-content: flex-end;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }

    .picker-header,
    .picker-footer {
      padding: 18px 20px;
      border-bottom: 1px solid var(--divider-color);
    }

    .picker-footer {
      border-bottom: 0;
      border-top: 1px solid var(--divider-color);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
    }

    .picker-title-row,
    .picker-actions {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }

    .picker-title {
      margin: 0;
      font-size: 1.1rem;
      font-weight: 700;
      color: var(--primary-text-color);
    }

    .picker-subtitle,
    .picker-current-path,
    .picker-empty {
      margin-top: 10px;
      color: var(--secondary-text-color);
      line-height: 1.5;
    }

    .picker-subtitle {
      margin-top: 6px;
    }

    .picker-pathbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      flex-wrap: wrap;
    }

    .picker-breadcrumbs {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      min-width: 0;
    }

    .picker-path-button {
      padding: 8px 12px;
      border-radius: 999px;
      border: 1px solid var(--divider-color);
      background: transparent;
      color: var(--primary-text-color);
      box-shadow: none;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 0.9rem;
    }

    .picker-path-separator {
      color: var(--secondary-text-color);
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    }

    .picker-content {
      padding: 18px 20px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      overflow: auto;
    }

    .picker-roots {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }

    .picker-roots-label {
      margin: 0;
      color: var(--secondary-text-color);
      font-weight: 700;
    }

    .picker-root,
    .picker-close {
      padding: 10px 14px;
      border-radius: 999px;
      border: 1px solid var(--divider-color);
      background: transparent;
      color: var(--primary-text-color);
      box-shadow: none;
    }

    .picker-root {
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }

    .picker-close {
      margin-left: auto;
    }

    .picker-list {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .picker-item {
      display: flex;
      align-items: center;
      gap: 12px;
      width: 100%;
      padding: 14px 16px;
      border-radius: 16px;
      border: 1px solid var(--divider-color);
      background: color-mix(in srgb, var(--secondary-background-color) 60%, transparent);
      color: inherit;
      cursor: pointer;
      text-align: left;
    }

    .picker-item-meta {
      min-width: 0;
      flex: 1 1 auto;
    }

    .picker-item-name {
      margin: 0;
      color: var(--primary-text-color);
      font-weight: 700;
      word-break: break-word;
    }

    .picker-item-path {
      margin-top: 4px;
      font-size: 0.9rem;
      color: var(--secondary-text-color);
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      word-break: break-all;
    }

    .picker-choose {
      min-width: 168px;
    }

    .picker-common-folders {
      display: flex;
      gap: 10px;
      flex-direction: row;
      align-items: center;
    }

    .advanced-toggle-row {
      display: flex;
      justify-content: flex-start;
      margin-top: 16px;
    }

    .advanced-toggle {
      padding: 10px 14px;
      border-radius: 999px;
      border: 1px solid var(--divider-color);
      background: transparent;
      color: var(--primary-text-color);
      box-shadow: none;
    }

    .advanced-fields {
      margin-top: 16px;
    }

    .picker-status {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
      margin-top: 20px 0px;
    }

    .picker-status-text {
      font-size: 0.9rem;
      color: var(--secondary-text-color);
    }

    .picker-status-text.valid {
      color: var(--success-color, #2e7d32);
    }

    .picker-status-text.invalid {
      color: var(--error-color, #d32f2f);
    }

    .picker-badges,
    .picker-item-badges {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }

    .picker-badge {
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      padding: 2px 10px;
      border-radius: 999px;
      background: color-mix(in srgb, var(--primary-color) 12%, transparent);
      color: var(--primary-color);
      font-size: 0.78rem;
      font-weight: 700;
      white-space: nowrap;
    }

    .picker-preview {
      padding: 14px 16px;
      border-radius: 16px;
      border: 1px solid var(--divider-color);
      background: color-mix(in srgb, var(--secondary-background-color) 60%, transparent);
    }

    .picker-preview-title {
      margin: 0 0 8px;
      color: var(--primary-text-color);
      font-size: 0.94rem;
      font-weight: 700;
    }

    .picker-preview-list {
      margin: 0;
      padding-left: 18px;
      color: var(--secondary-text-color);
      line-height: 1.5;
    }
    }

    @media (max-width: 1100px) {
      .field-grid {
        grid-template-columns: 1fr;
      }
    }

    @media (max-width: 600px) {
      .layout {
        padding: 16px;
      }

      .topbar {
        height: 56px;
        padding: 0 16px;
      }

      .topbar-notice {
        padding: 0 16px 12px;
      }

      .section {
        border-radius: 20px;
      }

      .section {
        padding: 18px;
      }

      .topbar-main {
        gap: 12px;
      }

      .topbar-actions {
        gap: 8px;
      }

      .input-row {
        flex-direction: column;
      }

      .picker-overlay {
        padding: 12px;
      }

      .picker-dialog {
        max-height: 88vh;
      }
    }
  </style>
  <div class="topbar-wrap" id="topbar"></div>
  <div class="layout" id="app"></div>
`;

class ChimeTtsSettingsPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this.shadowRoot.appendChild(template.content.cloneNode(true));
    this._app = this.shadowRoot.getElementById("app");
    this._topbar = this.shadowRoot.getElementById("topbar");
    this._data = null;
    this._draftValues = {};
    this._isDirty = false;
    this._clientErrors = {};
    this._loading = true;
    this._saving = false;
    this._saveResult = null;
    this._lastRequested = false;
    this._messageTimeout = null;
    this._saveResultTimeout = null;
    this._picker = null;
    this._pickerLoading = false;
    this._pickerError = null;
    this._advancedSections = {};
    this._pathValidationState = {};
    this._pathValidationTimers = {};
    this._invalidPathOverrides = {};
    this._restartPending = false;
    this._restartConfirmOpen = false;
    this._restarting = false;
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._lastRequested) {
      this._lastRequested = true;
      this._load();
      return;
    }
    if (!this._loading && !this._saving) {
      this._render();
    }
  }

  set panel(panel) {
    this._panel = panel;
  }

  set narrow(narrow) {
    const nextNarrow = Boolean(narrow);
    if (this._narrow === nextNarrow) {
      return;
    }
    this._narrow = nextNarrow;
    this.toggleAttribute("narrow", nextNarrow);
    if (!this._loading && !this._saving) {
      this._render();
    }
  }

  set route(route) {
    this._route = route;
  }

  async _load() {
    this._loading = true;
    this._render();
    try {
      this._data = await this._hass.callWS({ type: "chime_tts/get_settings" });
      this._draftValues = { ...(this._data?.values || {}) };
      this._isDirty = false;
      this._clientErrors = {};
      this._pathValidationState = this._buildInitialPathValidationState();
      this._invalidPathOverrides = {};
      this._restartPending = false;
      this._restartConfirmOpen = false;
      this._restarting = false;
    } catch (error) {
      this._data = {
        sections: [],
        values: {},
        errors: {},
        message: error?.message || "Unable to load Chime TTS settings.",
        message_type: "error",
        documentation_url: "https://nimroddolev.github.io/chime_tts/",
        logs_url: "/config/logs?filter=chime_tts",
        fallback_note: "",
        restart_note: "",
      };
      this._draftValues = {};
      this._isDirty = false;
      this._clientErrors = {};
      this._pathValidationState = {};
      this._invalidPathOverrides = {};
      this._restartPending = false;
      this._restartConfirmOpen = false;
      this._restarting = false;
    } finally {
      this._loading = false;
      this._render();
    }
  }

  _render() {
    if (this._loading) {
      this._renderTopbar({});
      this._app.innerHTML = `<div class="loading">Loading Chime TTS settings...</div>`;
      return;
    }

    const data = this._data || {};
    const sections = data.sections || [];
    const values = this._draftValues || {};
    const errors = { ...(data.errors || {}), ...(this._clientErrors || {}) };
    const message = data.message && data.message_type !== "success"
      ? `<div class="message ${this._escapeAttribute(data.message_type || "success")}">${this._escapeHtml(data.message)}</div>`
      : "";
    this._renderTopbar(data);

    this._app.innerHTML = `
      ${message}
      <form id="settings-form">
        ${sections.map((section) => this._renderSection(section, values, errors)).join("")}
        <div class="footer">
        </div>
      </form>
      ${this._renderPicker()}
      ${this._renderRestartConfirmation()}
    `;

    this.shadowRoot.getElementById("settings-form")?.addEventListener("submit", (event) => {
      event.preventDefault();
      this._submit();
    });
    this.shadowRoot.querySelectorAll("[data-reset-section]").forEach((button) => {
      button.addEventListener("click", (event) => this._resetSection(event.currentTarget.dataset.resetSection));
    });
    this.shadowRoot.querySelectorAll("[data-toggle-advanced]").forEach((button) => {
      button.addEventListener("click", (event) => this._toggleAdvanced(event.currentTarget.dataset.toggleAdvanced));
    });
    this.shadowRoot.querySelectorAll("[data-field]").forEach((field) => {
      const eventName = field.tagName === "SELECT" || field.type === "checkbox"
        ? "change"
        : "input";
      field.addEventListener(eventName, (event) => this._handleFieldChange(event));
    });
    this.shadowRoot.querySelectorAll("[data-browse-field]").forEach((button) => {
      button.addEventListener("click", (event) => this._openPicker(event.currentTarget.dataset.browseField));
    });
    this.shadowRoot.querySelectorAll("[data-picker-nav]").forEach((button) => {
      button.addEventListener("click", (event) => this._loadPicker(event.currentTarget.dataset.pickerNav));
    });
    this.shadowRoot.querySelectorAll("[data-picker-path]").forEach((button) => {
      button.addEventListener("click", (event) => this._loadPicker(event.currentTarget.dataset.pickerPath));
    });
    this.shadowRoot.querySelectorAll("[data-picker-root]").forEach((button) => {
      button.addEventListener("click", (event) => {
        event.preventDefault();
        this._loadPicker(event.currentTarget.dataset.pickerRoot);
      });
    });
    this.shadowRoot.querySelectorAll("[data-picker-open]").forEach((button) => {
      button.addEventListener("click", (event) => this._loadPicker(event.currentTarget.dataset.pickerOpen));
    });
    this.shadowRoot.querySelectorAll("[data-picker-close]").forEach((button) => {
      button.addEventListener("click", () => this._closePicker());
    });
    this.shadowRoot.querySelectorAll("[data-picker-choose]").forEach((button) => {
      button.addEventListener("click", (event) => this._choosePickerPath(event.currentTarget.dataset.pickerChoose));
    });
    this.shadowRoot.querySelectorAll("[data-restart-open]").forEach((button) => {
      button.addEventListener("click", () => this._openRestartConfirmation());
    });
    this.shadowRoot.querySelectorAll("[data-restart-cancel]").forEach((button) => {
      button.addEventListener("click", () => this._closeRestartConfirmation());
    });
    this.shadowRoot.querySelectorAll("[data-restart-confirm]").forEach((button) => {
      button.addEventListener("click", () => this._confirmRestart());
    });
    this.shadowRoot.querySelectorAll("[data-use-anyway]").forEach((button) => {
      button.addEventListener("click", (event) => this._useInvalidPathAnyway(event.currentTarget.dataset.useAnyway));
    });
    this.shadowRoot.querySelectorAll("[data-set-path]").forEach((link) => {
      link.addEventListener("click", (event) => {
        event.preventDefault();
        this._setPathSuggestion(
          event.currentTarget.dataset.setPath,
          event.currentTarget.dataset.pathValue,
        );
      });
    });
  }

  _renderTopbar(data) {
    this._topbar.innerHTML = `
      <div>
        <div class="topbar">
          <div class="topbar-main">
            <div class="topbar-text">
              <p class="topbar-title">
                <span>Chime TTS</span>
                <span class="topbar-version">${this._escapeHtml(String(data.version || ""))}</span>
              </p>
            </div>
          </div>
          <div class="topbar-actions">
            <a class="topbar-link" href="${this._escapeAttribute(data.documentation_url || "#")}" title="Open the documentation" target="_blank" rel="noreferrer">Help</a>
            <a class="topbar-link" href="${this._escapeAttribute(data.logs_url || "/config/logs?filter=chime_tts")}" title="Open the Chime TTS log messages">Logs</a>
            ${this._isDirty
              ? '<button class="button-secondary" type="button" data-reset-all="1">Reset Changes</button>'
              : ""
            }
            <div class="save-slot">
              ${this._saveResult
                ? `<span class="save-status ${this._escapeAttribute(this._saveResult)}" aria-live="polite">${this._saveResult === "success" ? "&#10003;" : "X"}</span>`
                : this._restartPending && !this._isDirty
                  ? `<button class="button-restart" type="button" data-restart-open="1" ${this._restarting ? "disabled" : ""}>Restart</button>`
                : `<button class="button-primary" id="save-top" type="button" ${this._saving || !this._isDirty || this._hasInvalidPathChanges() ? "disabled" : ""}>Save</button>`
              }
            </div>
          </div>
        </div>
      </div>
    `;
    this.shadowRoot.getElementById("save-top")?.addEventListener("click", () => this._submit());
    this.shadowRoot.querySelectorAll("[data-reset-all]").forEach((button) => {
      button.addEventListener("click", () => this._resetAllChanges());
    });
  }

  _renderSection(section, values, errors) {
    const sectionFields = section.fields || [];
    const basicFields = sectionFields.filter((field) => !field.advanced);
    const advancedFields = sectionFields.filter((field) => field.advanced);
    const isAdvancedOpen = this._isAdvancedOpen(section);
    const sectionDirty = this._isSectionDirty(section);
    return `
      <section class="section">
        <div class="section-header">
          <div class="section-header-copy">
            <h2>${this._escapeHtml(section.title)}</h2>
            <p>${this._escapeHtml(section.description || "")}</p>
          </div>
          ${sectionDirty ? `
            <div class="section-header-actions">
              <button
                class="button-secondary"
                type="button"
                data-reset-section="${this._escapeAttribute(section.key)}"
              >Reset Section</button>
            </div>
          ` : ""}
        </div>
        <div class="field-grid">
          ${basicFields.map((field) => this._renderField(field, values[field.key], errors[field.key])).join("")}
        </div>
        ${advancedFields.length > 0 ? `
          <div class="advanced-toggle-row">
            <button class="advanced-toggle" type="button" data-toggle-advanced="${this._escapeAttribute(section.key)}">
              ${isAdvancedOpen ? "Hide" : "Show"} Advanced
            </button>
          </div>
          ${isAdvancedOpen ? `
            <div class="field-grid advanced-fields">
              ${advancedFields.map((field) => this._renderField(field, values[field.key], errors[field.key])).join("")}
            </div>
          ` : ""}
        ` : ""}
      </section>
    `;
  }

  _renderField(field, value, error) {
    const fieldClasses = ["field"];
    if (field.wide) {
      fieldClasses.push("wide");
    }
    if (error) {
      fieldClasses.push("error");
    }
    const isChanged = this._isFieldChanged(field.key);
    if (isChanged) {
      fieldClasses.push("changed");
    }

    const control = field.type === "boolean"
      ? this._renderBoolean(field, value)
      : field.type === "select"
        ? this._renderSelect(field, value)
        : this._renderInput(field, value);
    const fieldIconUrl = field.icon_url || (field.key && OPTION_ICON_DATA_URLS[field.key]
      ? OPTION_ICON_DATA_URLS[field.key]
      : (field.key
        ? `/api/chime_tts/option_icons/${field.key}.svg`
        : ""));
    const normalizedFieldIconUrl = fieldIconUrl.startsWith("data:image/svg+xml;")
      ? fieldIconUrl.replaceAll("#", "%23")
      : fieldIconUrl;
    const savedCustomChimesPath = this._data?.values?.custom_chimes_path;
    const isCustomChimesPathChanged = field.key === "custom_chimes_path"
      && this._normalizeForCompare(value) !== this._normalizeForCompare(savedCustomChimesPath);
    const restartNote = isCustomChimesPathChanged
      ? `<div class="field-note">ℹ️  Restart Required<br />Any changes to the folder path or its contents will require a restart to take effect.</div>`
      : "";
    const providerHint = this._renderFieldSubhint(this._resolveProviderHint(field));
    const emptyDefaultHint = this._renderEmptyDefaultHint(field, value);
    const livePathValidation = this._renderPathValidation(field);
    const helpLink = field.docs_url
      ? `<a
          class="field-help-link"
          href="${this._escapeAttribute(field.docs_url)}"
          target="_blank"
          rel="noreferrer"
          aria-label="${this._escapeAttribute(`Open help for ${field.label}`)}"
          title="${this._escapeAttribute(`Open help for ${field.label}`)}"
        >?</a>`
      : "";

    return `
      <div class="${fieldClasses.join(" ")}">
        <div class="field-top">
          <div class="field-header">
            <img class="field-icon" src="${this._escapeAttribute(normalizedFieldIconUrl)}" alt="" loading="lazy" />
            <div class="field-copy">
              <div class="field-label-row">
                <p class="field-label">${this._escapeHtml(field.label)}</p>
                ${isChanged ? '<span class="field-changed-pill">Changed</span>' : ""}
                ${helpLink}
              </div>
              <p class="field-description">${this._escapeHtml(field.description || "")}</p>
            </div>
          </div>
          ${field.required ? '<span class="required">Required</span>' : ""}
        </div>
        ${control}
        ${providerHint}
        ${emptyDefaultHint}
        ${livePathValidation}
        ${restartNote}
        <div class="error-text">${error ? this._escapeHtml(this._formatError(error)) : ""}</div>
      </div>
    `;
  }

  _renderInput(field, value) {
    const type = field.type === "number" ? "number" : "text";
    const normalizedValue = value === null || value === undefined ? "" : value;
    const minAttr = field.min !== null && field.min !== undefined ? `min="${this._escapeAttribute(String(field.min))}"` : "";
    const stepAttr = type === "number" ? `step="${this._escapeAttribute(String(field.step || 1))}"` : "";
    const pathValidation = field.can_browse ? this._getPathValidationState(field) : null;
    const showInvalidIndicator = Boolean(
      field.can_browse
      && pathValidation
      && pathValidation.valid === false
      && String(normalizedValue).trim() !== ""
      && !this._invalidPathOverrides?.[field.key]
    );

    const inputMarkup = `
      <input
        class="control"
        data-field="${this._escapeAttribute(field.key)}"
        type="${type}"
        value="${this._escapeAttribute(String(normalizedValue))}"
        ${minAttr}
        ${stepAttr}
      />
    `;

    if (type !== "text" || !field.can_browse) {
      return inputMarkup;
    }

    return `
      <div class="input-row">
        ${inputMarkup}
        ${showInvalidIndicator
          ? `<button class="path-inline-action" type="button" data-use-anyway="${this._escapeAttribute(field.key)}">Use Anyway</button>`
          : ""
        }
        <button class="browse-button" type="button" data-browse-field="${this._escapeAttribute(field.key)}">Browse</button>
      </div>
    `;
  }

  _renderSelect(field, value) {
    const selectedValue = value === null || value === undefined ? "" : String(value);
    return `
      <select class="control-select" data-field="${this._escapeAttribute(field.key)}">
        ${(field.options || []).map((option) => {
          const optionValue = String(option.value ?? "");
          const selected = optionValue === selectedValue ? "selected" : "";
          return `<option value="${this._escapeAttribute(optionValue)}" ${selected}>${this._escapeHtml(option.label ?? optionValue)}</option>`;
        }).join("")}
      </select>
    `;
  }

  _renderBoolean(field, value) {
    return `
      <label class="control-checkbox">
        <input
          data-field="${this._escapeAttribute(field.key)}"
          type="checkbox"
          ${value ? "checked" : ""}
        />
        <span>Enabled</span>
      </label>
    `;
  }

  _renderFieldSubhint(hint) {
    if (!hint?.message) {
      return "";
    }
    const tone = hint.tone || "info";
    return `<div class="field-subhint ${this._escapeAttribute(tone)}">${this._escapeHtml(hint.message)}</div>`;
  }

  _resolveProviderHint(field) {
    if (!field) {
      return null;
    }

    const selectedProvider = field.key === "fallback_tts_platform_key"
      ? String(this._draftValues?.fallback_tts_platform_key || "").trim()
      : String(this._draftValues?.tts_platform_key || "").trim();

    if (!selectedProvider) {
      return field.provider_hint || null;
    }

    return field.provider_hints?.[selectedProvider] || field.provider_hint || null;
  }

  _renderEmptyDefaultHint(field, value) {
    if (!field.empty_default_hint || field.required || field.type === "boolean" || field.can_browse) {
      return "";
    }

    const normalized = value === null || value === undefined ? "" : String(value).trim();
    if (normalized !== "") {
      return "";
    }

    return `<div class="field-subhint muted">${this._escapeHtml(field.empty_default_hint)}</div>`;
  }

  _renderPathValidation(field) {
    if (!field.can_browse) {
      return "";
    }

    const validation = this._getPathValidationState(field);
    if (!validation?.message) {
      return "";
    }
    if (validation.valid && String(this._draftValues?.[field.key] || "").trim() !== "") {
      return "";
    }
    const suggestionLinks = (validation.suggestion_paths || []).length > 0
      ? `
        <div class="field-subhint-links">
          ${(validation.suggestion_paths || []).map((path) => `
            <a href="#" data-set-path="${this._escapeAttribute(field.key)}" data-path-value="${this._escapeAttribute(path)}">${this._escapeHtml(path)}</a>
          `).join("")}
        </div>
      `
      : "";

    return `
      <div class="field-subhint ${this._escapeAttribute(validation.tone || "muted")}">
        ${this._escapeHtml(validation.message)}
        ${suggestionLinks}
      </div>
    `;
  }

  _renderPicker() {
    if (!this._picker) {
      return "";
    }

    const directories = this._picker.directories || [];
    const roots = this._picker.roots || [];
    const loading = this._pickerLoading
      ? `<p class="picker-empty">Loading folders...</p>`
      : "";
    const error = this._pickerError
      ? `<div class="message error">${this._escapeHtml(this._pickerError)}</div>`
      : "";
    const empty = !this._pickerLoading && directories.length === 0
      ? `<p class="picker-empty">No subfolders were found in this location.</p>`
      : "";
    const breadcrumbs = this._renderBreadcrumbs(this._picker.current_path || "");
    const currentBadges = this._renderBadges(this._picker.current_path_badges || []);
    const preview = this._renderPickerPreview();
    const statusClass = this._picker.current_path_allowed ? "valid" : "invalid";

    return `
      <div class="picker-overlay">
        <div class="picker-dialog" role="dialog" aria-modal="true" aria-label="${this._escapeAttribute(this._picker.title || "Folder picker")}">
          <div class="picker-header">
            <div class="picker-title-row">
              <h3 class="picker-title">${this._escapeHtml(this._picker.title || "Select folder")}</h3>
              <button class="picker-close" type="button" data-picker-close="1">Close</button>
            </div>
            <p class="picker-subtitle">Browse folders that are visible inside the Home Assistant container, then choose one to fill this field.</p>
            <div class="picker-common-folders">
              <p class="picker-roots-label">Common folders:</p>
              ${roots.length > 0 ? `
                <div class="picker-roots">
                  ${roots.map((root) => `
                    <a href="#" data-picker-root="${this._escapeAttribute(root.path)}">
                      ${this._escapeHtml(root.name)}
                    </a>
                  `).join("")}
                </div>
              ` : ""
              }
            </div>
          </div>
          <div class="picker-content">
            ${error}
            <div class="picker-pathbar">
              <div class="picker-breadcrumbs">
                ${breadcrumbs}
              </div>
              <button
                class="button-primary picker-choose"
                type="button"
                data-picker-choose="${this._escapeAttribute(this._picker.current_path || "")}"
                ${this._picker.current_path_allowed ? "" : "disabled"}
              >Select</button>
            </div>
            <div class="picker-status">
              <span class="picker-status-text ${statusClass}">${this._escapeHtml(this._picker.current_path_validation_message || "")}</span>
              ${currentBadges ? `<div class="picker-badges">${currentBadges}</div>` : ""}
            </div>
            ${loading}
            ${directories.length > 0 ? `
              <div class="picker-list">
                ${directories.map((directory) => `
                  <button class="picker-item" type="button" data-picker-open="${this._escapeAttribute(directory.path)}">
                    <div class="picker-item-meta">
                      <p class="picker-item-name">${this._escapeHtml(directory.name)}</p>
                      <p class="picker-item-path">${this._escapeHtml(directory.path)}</p>
                      ${(directory.badges || []).length > 0
                        ? `<div class="picker-item-badges">${this._renderBadges(directory.badges)}</div>`
                        : ""
                      }
                    </div>
                  </button>
                `).join("")}
              </div>
            ` : ""}
            ${empty}
            ${preview}
          </div>
        </div>
      </div>
    `;
  }

  _renderRestartConfirmation() {
    if (!this._restartConfirmOpen) {
      return "";
    }

    return `
      <div class="confirm-overlay">
        <div class="confirm-dialog" role="dialog" aria-modal="true" aria-label="Confirm Home Assistant restart">
          <h3 class="confirm-title">Restart Home Assistant?</h3>
          <p class="confirm-copy">
            The custom chimes folder change has been saved, but it will not take effect until Home Assistant restarts.
          </p>
          <div class="confirm-actions">
            <button class="button-secondary" type="button" data-restart-cancel="1" ${this._restarting ? "disabled" : ""}>Cancel</button>
            <button class="button-primary" type="button" data-restart-confirm="1" ${this._restarting ? "disabled" : ""}>
              ${this._restarting
                ? '<span class="button-spinner" aria-hidden="true"></span>'
                : "Restart Home Assistant"
              }
            </button>
          </div>
        </div>
      </div>
    `;
  }

  _renderBadges(badges) {
    return (badges || []).map((badge) => `<span class="picker-badge">${this._escapeHtml(badge)}</span>`).join("");
  }

  _renderPickerPreview() {
    if (this._picker?.field_key !== "custom_chimes_path") {
      return "";
    }

    const previewFiles = this._picker?.preview_files || [];
    return `
      <div class="picker-preview">
        ${previewFiles.length > 0 ? `
          <p class="picker-preview-title">
            ${previewFiles.length} Audio file${previewFiles.length > 1 ? "s" : ""} found:
          </p>
          <ul class="picker-preview-list">
            ${previewFiles.map((fileName) => `
            <li>
              ${this._escapeHtml(fileName)}
            </li>`).join("")}
          </ul>` :

          `<p class="picker-empty">
            No audio files were found in this folder.
          </p>`
        }
      </div>`;
  }

  _renderBreadcrumbs(path) {
    const segments = this._buildPathSegments(path);
    return segments.map((segment, index) => {
      const separator = index === 0
        ? ""
        : '<span class="picker-path-separator">/</span>';
      return `${separator}<button class="picker-path-button" type="button" data-picker-path="${this._escapeAttribute(segment.path)}">${this._escapeHtml(segment.label)}</button>`;
    }).join("");
  }

  _buildPathSegments(path) {
    const normalized = String(path || "").trim();
    if (!normalized) {
      return [];
    }

    const clean = normalized.endsWith("/") && normalized !== "/" ? normalized.slice(0, -1) : normalized;
    const parts = clean.split("/").filter(Boolean);
    const segments = [{ label: "root", path: "/" }];
    let current = "";

    for (const part of parts) {
      current += `/${part}`;
      segments.push({
        label: part,
        path: `${current}/`,
      });
    }

    return segments;
  }

  _buildInitialPathValidationState() {
    const state = {};
    for (const section of this._data?.sections || []) {
      for (const field of section.fields || []) {
        if (field.can_browse && field.path_validation) {
          state[field.key] = field.path_validation;
        }
      }
    }
    return state;
  }

  _getPathValidationState(field) {
    if (!field?.can_browse) {
      return null;
    }
    return this._pathValidationState?.[field.key] || field.path_validation || null;
  }

  _schedulePathValidation(fieldKey, path) {
    if (!fieldKey) {
      return;
    }

    const existingTimer = this._pathValidationTimers?.[fieldKey];
    if (existingTimer) {
      window.clearTimeout(existingTimer);
    }

    this._pathValidationTimers = {
      ...(this._pathValidationTimers || {}),
      [fieldKey]: window.setTimeout(() => {
        delete this._pathValidationTimers[fieldKey];
        this._requestPathValidation(fieldKey, path);
      }, 250),
    };
  }

  async _requestPathValidation(fieldKey, path) {
    if (!fieldKey) {
      return;
    }

    try {
      const validation = await this._hass.callWS({
        type: "chime_tts/validate_path",
        field_key: fieldKey,
        path: String(path ?? ""),
      });
      this._pathValidationState = {
        ...(this._pathValidationState || {}),
        [fieldKey]: validation,
      };
      this._rerenderPreservingInputState();
    } catch (error) {
      this._pathValidationState = {
        ...(this._pathValidationState || {}),
        [fieldKey]: {
          field_key: fieldKey,
          valid: false,
          tone: "error",
          message: error?.message || "Unable to validate this folder path right now.",
          badges: [],
        },
      };
      this._rerenderPreservingInputState();
    }
  }

  _rerenderPreservingInputState(fieldKey = null) {
    const scrollElement = document.scrollingElement;
    const scrollTop = scrollElement?.scrollTop ?? window.scrollY ?? 0;
    const activeElement = this.shadowRoot.activeElement;
    const activeFieldKey = fieldKey || activeElement?.dataset?.field || null;
    const selectionStart = typeof activeElement?.selectionStart === "number"
      ? activeElement.selectionStart
      : null;
    const selectionEnd = typeof activeElement?.selectionEnd === "number"
      ? activeElement.selectionEnd
      : null;

    this._render();
    window.requestAnimationFrame(() => {
      if (scrollElement) {
        scrollElement.scrollTop = scrollTop;
      } else {
        window.scrollTo(0, scrollTop);
      }

      if (!activeFieldKey) {
        return;
      }

      const nextField = this.shadowRoot.querySelector(`[data-field="${CSS.escape(activeFieldKey)}"]`);
      if (!nextField) {
        return;
      }

      nextField.focus({ preventScroll: true });
      if (selectionStart !== null && selectionEnd !== null && typeof nextField.setSelectionRange === "function") {
        nextField.setSelectionRange(selectionStart, selectionEnd);
      }
    });
  }

  _openRestartConfirmation() {
    if (!this._restartPending || this._restarting) {
      return;
    }
    this._restartConfirmOpen = true;
    this._render();
  }

  _closeRestartConfirmation() {
    if (this._restarting) {
      return;
    }
    this._restartConfirmOpen = false;
    this._render();
  }

  async _confirmRestart() {
    if (!this._restartPending || this._restarting) {
      return;
    }

    this._restarting = true;
    this._render();

    try {
      await this._hass.callService("homeassistant", "restart");
      this._restartPending = false;
      this._restartConfirmOpen = false;
      this._data = {
        ...(this._data || {}),
        message: "Home Assistant restart requested.",
        message_type: "success",
      };
      this._showSaveResult("success");
    } catch (error) {
      this._data = {
        ...(this._data || {}),
        message: error?.message || "Unable to request a Home Assistant restart.",
        message_type: "error",
      };
      this._showSaveResult("error");
    } finally {
      this._restarting = false;
      this._render();
    }
  }

  _resetAllChanges() {
    this._draftValues = { ...(this._data?.values || {}) };
    this._clientErrors = {};
    this._isDirty = false;
    this._pathValidationState = this._buildInitialPathValidationState();
    this._invalidPathOverrides = {};
    this._restartPending = false;
    this._restartConfirmOpen = false;
    this._clearSaveResult();
    this._render();
  }

  _resetSection(sectionKey) {
    if (!sectionKey) {
      return;
    }

    const section = (this._data?.sections || []).find((item) => item.key === sectionKey);
    if (!section) {
      return;
    }

    const nextDraftValues = { ...(this._draftValues || {}) };
    for (const field of section.fields || []) {
      nextDraftValues[field.key] = this._data?.values?.[field.key];
      if (this._clientErrors[field.key]) {
        delete this._clientErrors[field.key];
      }
      if (field.can_browse && field.path_validation) {
        this._pathValidationState = {
          ...(this._pathValidationState || {}),
          [field.key]: field.path_validation,
        };
      }
      if (field.can_browse && this._invalidPathOverrides?.[field.key]) {
        const nextOverrides = { ...(this._invalidPathOverrides || {}) };
        delete nextOverrides[field.key];
        this._invalidPathOverrides = nextOverrides;
      }
    }
    this._draftValues = nextDraftValues;
    this._isDirty = this._hasValueChanges();
    if (section.fields?.some((field) => field.key === "custom_chimes_path")) {
      this._restartPending = false;
      this._restartConfirmOpen = false;
    }
    this._render();
  }

  _toggleAdvanced(sectionKey) {
    if (!sectionKey) {
      return;
    }
    const section = (this._data?.sections || []).find((item) => item.key === sectionKey);
    this._advancedSections = {
      ...(this._advancedSections || {}),
      [sectionKey]: !this._isAdvancedOpen(section || { key: sectionKey, fields: [] }),
    };
    this._render();
  }

  _isAdvancedOpen(section) {
    const explicit = this._advancedSections?.[section.key];
    if (explicit !== undefined) {
      return explicit;
    }
    return this._shouldAutoExpandSection(section);
  }

  _shouldAutoExpandSection(section) {
    const advancedFields = (section.fields || []).filter((field) => field.advanced);
    if (advancedFields.some((field) => this._isFieldChanged(field.key))) {
      return true;
    }
    if (section.key === "voice") {
      const platformValue = this._draftValues?.tts_platform_key;
      if (platformValue && String(platformValue).trim() !== "") {
        return true;
      }
      return advancedFields.some((field) => {
        const value = this._draftValues?.[field.key];
        return value !== null && value !== undefined && String(value).trim() !== "";
      });
    }
    return false;
  }

  _isSectionDirty(section) {
    return (section.fields || []).some((field) => this._isFieldChanged(field.key));
  }

  _isFieldChanged(fieldKey) {
    const savedValues = this._data?.values || {};
    const draftValues = this._draftValues || {};
    return this._normalizeForCompare(savedValues[fieldKey]) !== this._normalizeForCompare(draftValues[fieldKey]);
  }

  _getRestartRequiredChangedFields() {
    const restartKeys = this._data?.restart_required_field_keys || [];
    const labels = new Map();
    for (const section of this._data?.sections || []) {
      for (const field of section.fields || []) {
        labels.set(field.key, field.label);
      }
    }
    return restartKeys
      .filter((fieldKey) => this._isFieldChanged(fieldKey))
      .map((fieldKey) => ({ key: fieldKey, label: labels.get(fieldKey) || fieldKey }));
  }

  _useInvalidPathAnyway(fieldKey) {
    if (!fieldKey) {
      return;
    }
    this._invalidPathOverrides = {
      ...(this._invalidPathOverrides || {}),
      [fieldKey]: true,
    };
    this._render();
  }

  _setPathSuggestion(fieldKey, path) {
    if (!fieldKey || !path) {
      return;
    }
    const nextOverrides = { ...(this._invalidPathOverrides || {}) };
    delete nextOverrides[fieldKey];
    this._invalidPathOverrides = nextOverrides;
    this._draftValues = {
      ...(this._draftValues || {}),
      [fieldKey]: path,
    };
    this._isDirty = this._hasValueChanges();
    this._schedulePathValidation(fieldKey, path);
    this._rerenderPreservingInputState(fieldKey);
  }

  async _submit() {
    if (this._saving || !this._isDirty || this._hasInvalidPathChanges()) {
      return;
    }

    this._clientErrors = this._validateRequiredFields();
    if (Object.keys(this._clientErrors).length > 0) {
      this._render();
      return;
    }

    const values = { ...this._draftValues };
    this._saving = true;
    this._clearSaveResult();
    this._render();

    try {
      this._data = await this._hass.callWS({
        type: "chime_tts/save_settings",
        values,
        allow_invalid_paths: Object.keys(this._invalidPathOverrides || {}).filter((fieldKey) => this._invalidPathOverrides[fieldKey]),
      });
      this._draftValues = { ...(this._data?.values || {}) };
      this._isDirty = false;
      this._clientErrors = {};
      this._pathValidationState = this._buildInitialPathValidationState();
      this._invalidPathOverrides = {};
      this._restartPending = Boolean(this._data?.restart_required);
      this._restartConfirmOpen = false;
      if (this._restartPending) {
        this._clearSaveResult();
      } else if (this._data?.message_type === "success" && this._data?.message) {
        this._showSaveResult("success");
        this._scheduleMessageClear();
      }
    } catch (error) {
      this._data = {
        ...(this._data || {}),
        message: error?.message || "Unable to save Chime TTS settings.",
        message_type: "error",
      };
      this._showSaveResult("error");
    } finally {
      this._saving = false;
      this._render();
    }
  }

  _handleFieldChange(event) {
    const field = event.currentTarget;
    const key = field?.dataset?.field;
    if (!key) {
      return;
    }

    const nextValue = field.type === "checkbox" ? field.checked : field.value;
    if (key === "custom_chimes_path") {
      this._restartPending = false;
      this._restartConfirmOpen = false;
    }
    if (this._invalidPathOverrides?.[key]) {
      const nextOverrides = { ...(this._invalidPathOverrides || {}) };
      delete nextOverrides[key];
      this._invalidPathOverrides = nextOverrides;
    }
    this._draftValues = {
      ...(this._draftValues || {}),
      [key]: nextValue,
    };
    if (this._clientErrors[key]) {
      const nextErrors = { ...(this._clientErrors || {}) };
      delete nextErrors[key];
      this._clientErrors = nextErrors;
    }
    this._isDirty = this._hasValueChanges();
    if (this._isPathFieldKey(key)) {
      this._schedulePathValidation(key, nextValue);
    }
    this._rerenderPreservingInputState(key);
  }

  async _openPicker(fieldKey) {
    if (!fieldKey || this._pickerLoading) {
      return;
    }
    this._picker = {
      field_key: fieldKey,
      title: this._findFieldLabel(fieldKey),
      current_path: this._draftValues?.[fieldKey] || "",
      parent_path: null,
      roots: [],
      directories: [],
    };
    this._pickerError = null;
    this._pickerLoading = true;
    this._render();
    await this._loadPicker(this._draftValues?.[fieldKey] || "", fieldKey);
  }

  _closePicker() {
    this._picker = null;
    this._pickerLoading = false;
    this._pickerError = null;
    this._render();
  }

  async _loadPicker(path, fieldKey = null) {
    const targetFieldKey = fieldKey || this._picker?.field_key;
    if (!targetFieldKey) {
      return;
    }

    this._pickerLoading = true;
    this._pickerError = null;
    this._render();

    try {
      const pickerData = await this._hass.callWS({
        type: "chime_tts/browse_path",
        field_key: targetFieldKey,
        path,
      });
      this._picker = pickerData;
    } catch (error) {
      this._pickerError = error?.message || "Unable to browse folders.";
    } finally {
      this._pickerLoading = false;
      this._render();
    }
  }

  _choosePickerPath(path) {
    const fieldKey = this._picker?.field_key;
    if (!fieldKey || !path) {
      return;
    }

    this._draftValues = {
      ...(this._draftValues || {}),
      [fieldKey]: path,
    };
    if (this._invalidPathOverrides?.[fieldKey]) {
      const nextOverrides = { ...(this._invalidPathOverrides || {}) };
      delete nextOverrides[fieldKey];
      this._invalidPathOverrides = nextOverrides;
    }
    this._pathValidationState = {
      ...(this._pathValidationState || {}),
      [fieldKey]: {
        field_key: fieldKey,
        path,
        valid: Boolean(this._picker?.current_path_allowed),
        exists: true,
        tone: this._picker?.current_path_allowed ? "success" : "error",
        message: this._picker?.current_path_validation_message || "",
        badges: this._picker?.current_path_badges || [],
      },
    };
    if (this._clientErrors[fieldKey]) {
      const nextErrors = { ...(this._clientErrors || {}) };
      delete nextErrors[fieldKey];
      this._clientErrors = nextErrors;
    }
    this._isDirty = this._hasValueChanges();
    this._closePicker();
  }

  _findFieldLabel(fieldKey) {
    const sections = this._data?.sections || [];
    for (const section of sections) {
      for (const field of section.fields || []) {
        if (field.key === fieldKey) {
          return field.label;
        }
      }
    }
    return "Select folder";
  }

  _isPathFieldKey(fieldKey) {
    const sections = this._data?.sections || [];
    for (const section of sections) {
      for (const field of section.fields || []) {
        if (field.key === fieldKey) {
          return Boolean(field.can_browse);
        }
      }
    }
    return false;
  }

  _hasInvalidPathChanges() {
    const sections = this._data?.sections || [];
    for (const section of sections) {
      for (const field of section.fields || []) {
        if (
          !field.can_browse
          || !this._isFieldChanged(field.key)
          || this._invalidPathOverrides?.[field.key]
        ) {
          continue;
        }
        const validation = this._getPathValidationState(field);
        const value = String(this._draftValues?.[field.key] ?? "").trim();
        if (value !== "" && validation?.valid === false) {
          return true;
        }
      }
    }
    return false;
  }

  _hasValueChanges() {
    const savedValues = this._data?.values || {};
    const draftValues = this._draftValues || {};
    const keys = new Set([...Object.keys(savedValues), ...Object.keys(draftValues)]);

    for (const key of keys) {
      if (this._normalizeForCompare(savedValues[key]) !== this._normalizeForCompare(draftValues[key])) {
        return true;
      }
    }

    return false;
  }

  _normalizeForCompare(value) {
    if (value === null || value === undefined) {
      return "";
    }
    if (typeof value === "boolean") {
      return value ? "true" : "false";
    }
    return String(value);
  }

  _validateRequiredFields() {
    const errors = {};
    const sections = this._data?.sections || [];
    for (const section of sections) {
      for (const field of section.fields || []) {
        if (!field.required) {
          continue;
        }
        const value = this._draftValues?.[field.key];
        if (field.type === "boolean") {
          continue;
        }
        if (value === null || value === undefined || String(value).trim() === "") {
          errors[field.key] = "required";
        }
      }
    }
    return errors;
  }

  _scheduleMessageClear() {
    if (this._messageTimeout) {
      window.clearTimeout(this._messageTimeout);
    }
    this._messageTimeout = window.setTimeout(() => {
      if (!this._data?.message || this._data?.message_type !== "success") {
        return;
      }
      this._data = {
        ...this._data,
        message: null,
        message_type: null,
      };
      this._messageTimeout = null;
      this._render();
    }, 5000);
  }

  _clearSaveResult() {
    this._saveResult = null;
    if (this._saveResultTimeout) {
      window.clearTimeout(this._saveResultTimeout);
      this._saveResultTimeout = null;
    }
  }

  _showSaveResult(result) {
    this._clearSaveResult();
    this._saveResult = result;
    this._saveResultTimeout = window.setTimeout(() => {
      this._saveResult = null;
      this._saveResultTimeout = null;
      this._renderTopbar(this._data || {});
    }, 1500);
  }

  _formatError(errorKey) {
    const errorMap = {
      required: "This field is required.",
      invalid_number: "Enter a valid number.",
      timeout: "The timeout value is invalid.",
      timeout_sub: "Enter a valid timeout duration.",
      tts_platform_none: "No TTS platforms were detected. Add at least one TTS integration first.",
      tts_platform_select: "The selected TTS platform was not found.",
      temp_path: "The temp folder must be inside a configured media directory.",
      www_path: "The say_url output folder must be inside an external directory, /media, or /config/www.",
    };
    return errorMap[errorKey] || errorKey;
  }

  _escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  _escapeAttribute(value) {
    return this._escapeHtml(value);
  }
}

if (!customElements.get(PANEL_TAG)) {
  customElements.define(PANEL_TAG, ChimeTtsSettingsPanel);
}
