# <Brand> design pack

Map the brand's colours and fonts to the roles in `references/design-system.md`. One
preset is enough to start; add a second only for a clearly different mood.

## Preset A: <name>

### Roles

| Role | Token | Hex |
|---|---|---|
| `ground` | | |
| `text` | | |
| `dark` | | |
| `primary` | | |
| `surface` | | |
| `highlight` | | |
| `muted` | | |
| `mutedDark` | | |
| `rule` | | |

| Role | Font |
|---|---|
| `display` | |
| `displayRegular` / `displayItalic` | |
| `body`, `bodyMedium`, `bodyBold` | |
| `label` | |
| `arrow` | a font with `→` |

Contrast checked: text on `ground` __:1, text on `dark` __:1 (aim for 4.5:1 or better).

## Colour schemes

Add schemes as the brand grows: the same roles, other values from the brand's palette
plus neutral black and white (a light one, a dark one, a loud one on the accent colour).
Each needs `onDark` (light text on dark grounds) and a duotone pair. Give each series its
own scheme; one-off pieces rotate (`references/design-variety.md` section 2b). Check text
on ground and muted on ground at 4.5:1, big numbers on ground at 3:1.

Duotone pair for photos: highlight `#______` over shadow `#______`.

### BRAND block for `scripts/figma-helpers.js`

```js
const BRAND = {
  site: 'example.com',
  handle: '@brand',
  logo: { letter: 'B', wordmark: 'Brand' }, // with the brand's file: image: 'assets/logos/logo.svg', imageOnDark: 'assets/logos/logo-white.svg'
  swipe: 'GESER  →',
  end: 'SELESAI',
  sourcesLabel: 'SUMBER',
  scheme: 'utama',
  schemes: {
    utama: { ground: '#FFFFFF', text: '#111111', dark: '#111111', onDark: '#FFFFFF', primary: '#1A3D7C', surface: '#EEF1F5', highlight: '#FFD84D', muted: '#5C6670', mutedDark: '#A7B0B8', rule: '#DDE2E7',
      duotone: { light: ['#EEF1F5', '#1A3D7C'], dark: ['#A7B0B8', '#111111'] } },
    gelap: { ground: '#111111', text: '#F5F5F2', dark: '#000000', onDark: '#F5F5F2', primary: '#FFD84D', surface: '#1E1F22', highlight: '#FFD84D', muted: '#9A9EA4', mutedDark: '#9A9EA4', rule: '#2C2E33',
      duotone: { light: ['#9A9EA4', '#111111'], dark: ['#9A9EA4', '#000000'] } },
  },
  fonts: {
    display: { family: 'Inter', style: 'Bold' }, displayRegular: { family: 'Inter', style: 'Regular' }, displayItalic: { family: 'Inter', style: 'Italic' },
    body: { family: 'Inter', style: 'Regular' }, bodyMedium: { family: 'Inter', style: 'Medium' }, bodyBold: { family: 'Inter', style: 'Bold' },
    label: { family: 'Roboto Mono', style: 'Regular' }, arrow: { family: 'Inter', style: 'Medium' },
  },
};
```

## Logo lockup

- File or construction:
- Minimum size and clear space:
- On light / on dark:

## Files

| | |
|---|---|
| Figma file for social content | |
| Site source or brand guide | |
