export const EMPTY_CHIME_SET_SLOT_MACHINE_STYLES = String.raw`
  .chime-sets-empty-state { display:flex; align-items:center; justify-content:center; gap:clamp(10px,2vw,24px); min-height:250px; padding:18px 0 8px; }
  .chime-slot-machine { position:relative; width:min(100%,300px); flex:0 1 300px; overflow:visible; }
  .chime-slot-machine .slot-reel-strip { will-change:transform; animation:chimeSlotReelSpin 2.97s infinite both; }
  .chime-slot-machine .slot-handle { transform-box:view-box; transform-origin:226px 112px; animation:chimeSlotHandleTurn 2.97s ease-in-out infinite both; }
  .chime-slot-message { position:relative; max-width:280px; margin:0; padding:21px 24px; border:2px solid color-mix(in srgb,#173f71 72%,var(--divider-color)); border-radius:18px; background:color-mix(in srgb,var(--card-background-color) 88%,white 12%); color:var(--primary-text-color); font-size:clamp(1.1rem,2.2vw,1.35rem); font-weight:700; line-height:1.35; box-shadow:0 10px 18px rgba(23,63,113,.12); }
  .chime-slot-message::before { content:""; position:absolute; left:-12px; top:50%; width:20px; height:20px; border-bottom:2px solid color-mix(in srgb,#173f71 72%,var(--divider-color)); border-left:2px solid color-mix(in srgb,#173f71 72%,var(--divider-color)); background:inherit; transform:translateY(-50%) rotate(45deg); }
  @keyframes chimeSlotReelSpin {
    0%, 15% { transform:translateY(0); }
    15% { animation-timing-function:cubic-bezier(.18,.8,.35,1); }
    100% { transform:translateY(840px); }
  }
  @keyframes chimeSlotHandleTurn { 0%,3%,100% { transform:rotate(0deg); } 15% { transform:rotate(34deg); } 25% { transform:rotate(0deg); } }
  @media (max-width:620px) { .chime-sets-empty-state { flex-direction:column; gap:8px; } .chime-slot-message { max-width:310px; text-align:center; } .chime-slot-message::before { left:50%; top:-12px; transform:translateX(-50%) rotate(135deg); } }
  @media (prefers-reduced-motion:reduce) { .chime-slot-machine .slot-reel-strip,.chime-slot-machine .slot-handle { animation:none; } }
`;

const ICON_PITCH = 70;

const renderIcon = (icon) => {
  if (icon === "bell") return '<path d="M142 82c-12 0-21 10-21 22v14l-7 9h56l-7-9v-14c0-12-9-22-21-22Z" fill="#ffd83d" stroke="#153f71" stroke-width="5" stroke-linejoin="round"/><path d="M134 130c2 8 14 8 16 0" fill="none" stroke="#153f71" stroke-width="5" stroke-linecap="round"/>';
  if (icon === "note") return '<path d="M130 88 165 80v16l-35 8Z" fill="#4b83dc" stroke="#153f71" stroke-width="5" stroke-linejoin="round"/><path d="M130 96v34m35-42v33" fill="none" stroke="#153f71" stroke-width="5" stroke-linecap="round"/><ellipse cx="121" cy="130" rx="11" ry="8" fill="#4b83dc" stroke="#153f71" stroke-width="5"/><ellipse cx="156" cy="122" rx="11" ry="8" fill="#4b83dc" stroke="#153f71" stroke-width="5"/>';
  return '<path d="M118 105v10m12-20v30m12-37v44m12-37v30m12-20v10" fill="none" stroke="#4b83dc" stroke-width="7" stroke-linecap="round"/>';
};

export const renderEmptyChimeSetSlotMachine = (restingSelection, winningSelection) => {
  const icons = ["bell", "note", "waves"];
  const strip = Array.from({ length:31 }, (_, index) => {
    const offset = index - 15;
    const icon = offset === 0
      ? icons[restingSelection]
      : offset === -12
        ? icons[winningSelection]
        : icons[(winningSelection + offset + 12 + icons.length) % icons.length];
    return `<g transform="translate(0 ${(offset * ICON_PITCH) - 10})">${renderIcon(icon)}</g>`;
  }).join("");
  return `<div class="chime-sets-empty-state"><div class="chime-slot-machine"><svg viewBox="0 0 300 270" role="img" aria-label="An animated single-reel chime slot machine" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="slot-gold" x1="0" x2="1"><stop stop-color="#b96900"/><stop offset=".42" stop-color="#ffd36a"/><stop offset="1" stop-color="#bd7308"/></linearGradient><linearGradient id="slot-pink" x1="0" x2="0" y2="1"><stop stop-color="#e90061"/><stop offset="1" stop-color="#a90050"/></linearGradient><clipPath id="chime-slot-window"><rect x="84" y="63" width="117" height="75" rx="13"/></clipPath></defs><path d="M61 43h166v24H61z" fill="url(#slot-gold)" stroke="#9a5100" stroke-width="4"/><path d="M68 28h152v15H68z" fill="#e90061" stroke="#a90050" stroke-width="4"/><path d="M57 68c0-17 14-29 31-29h110c17 0 31 12 31 29v65c0 13-10 23-23 23H80c-13 0-23-10-23-23Z" fill="url(#slot-gold)" stroke="#9a5100" stroke-width="5"/><path d="M79 61h126v82H79z" fill="#fff8fa" stroke="#d7c5ca" stroke-width="4"/><rect x="84" y="63" width="117" height="75" rx="13" fill="#fff"/><g clip-path="url(#chime-slot-window)"><g class="slot-reel-strip">${strip}</g></g><path d="M62 151h164v72H62z" fill="url(#slot-pink)" stroke="#9e0050" stroke-width="5"/><path d="M72 170h143v43H72z" fill="none" stroke="#ffc43d" stroke-width="4"/><g class="slot-handle"><path d="M226 112 248 57" fill="none" stroke="#873c00" stroke-width="8" stroke-linecap="round"/><path d="M226 112 248 57" fill="none" stroke="#ffc64e" stroke-width="4" stroke-linecap="round"/><circle cx="251" cy="50" r="12" fill="#d90055" stroke="#9e0050" stroke-width="4"/></g></svg></div><blockquote class="chime-slot-message">“Move the washing to the dryer”</blockquote></div>`;
};
