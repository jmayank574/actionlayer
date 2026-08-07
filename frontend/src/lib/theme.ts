// Chart/SVG colors mirroring the CSS tokens in index.css's @theme block.
// Duplicated as plain hex because recharts needs literal color strings, not
// CSS custom properties, in some of its SVG props. Keep these two in sync.

export const COLORS = {
  cream: '#faf7f2',
  creamRaised: '#fffefb',
  rust: '#8f3350',
  rustBar: '#ecc9d2',
  rustDark: '#5e2035',
  sage: '#6b8a5a',
  sageBar: '#d6e2ca',
  sageDark: '#3f5337',
  amber: '#b45309',
  ink: '#292524', // stone-800
  inkSoft: '#78716c', // stone-500
} as const
