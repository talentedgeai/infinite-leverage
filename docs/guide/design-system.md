# IL8 Design System — HTML Reference

Apply these tokens to every HTML file in the Infinite Leverage blueprint project.
Source: https://infiniteleverage-8.com/

---

## CSS Variables

```css
:root {
  /* Backgrounds */
  --ink:        #02081c;   /* page background */
  --ink-2:      #060f2c;   /* card surface */
  --ink-3:      #0a1740;   /* elevated surface */

  /* Text */
  --paper:      #eaeef2;   /* primary text */
  --muted:      #eaeef29e; /* secondary text */
  --rule:       #eaeef21f; /* subtle border */
  --rule-2:     #eaeef212; /* faint border */

  /* Accent colours */
  --accent:     #6ff2c1;   /* mint green — primary CTA */
  --accent-deep:#1a9e74;   /* mint hover */
  --accent-2:   #287be8;   /* blue */
  --pink:       #d1458b;
  --amber:      #f0a500;
  --orange:     #e8682b;

  /* Typography */
  --serif: "Fraunces", Georgia, serif;
  --sans:  "Inter", -apple-system, sans-serif;
  --mono:  "JetBrains Mono", ui-monospace, monospace;

  /* Layout */
  --maxw: 1280px;
}
```

## Google Fonts Import

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;1,9..144,300&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

---

## Key Patterns

### Page base

```css
body {
  font-family: var(--sans);
  background: var(--ink);
  color: var(--paper);
  margin: 0;
}
```

### Sticky nav

```css
nav {
  position: sticky;
  top: 0;
  height: 64px;
  background: #02081cdb;
  backdrop-filter: blur(14px);
  border-bottom: 1px solid var(--rule);
  display: flex;
  align-items: center;
  z-index: 100;
}
```

### Pill buttons

```css
.btn {
  font-family: var(--mono);
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: .08em;
  padding: 16px 26px;
  border-radius: 999px;
  border: none;
  cursor: pointer;
}
.btn-primary { background: var(--accent); color: var(--ink); }
.btn-outline  { background: transparent; border: 1px solid var(--rule); color: var(--paper); }
```

### Eyebrow labels

```css
.eyebrow {
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: .18em;
  color: var(--muted);
}
```

### Headings

```css
h1, h2 { font-family: var(--serif); font-weight: 300; }
h3, h4  { font-family: var(--sans);  font-weight: 600; }
```

### Cards

```css
.card {
  background: var(--ink-2);
  border: 1px solid var(--rule-2);
  border-radius: 10px;
  padding: 24px;
}
```

### Tab nav

```css
.tab-btn {
  font-family: var(--mono);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: .08em;
  padding: 12px 18px;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--muted);
  cursor: pointer;
}
.tab-btn.active {
  color: var(--accent);
  border-bottom-color: var(--accent);
}
```

### Code / monospace blocks

```css
pre, code {
  font-family: var(--mono);
  background: var(--ink-3);
  border: 1px solid var(--rule);
  border-radius: 6px;
  font-size: 13px;
}
pre  { padding: 16px; overflow-x: auto; }
code { padding: 2px 6px; }
```

---

## Agent Colour Map

| Agent | Colour | Variable |
|---|---|---|
| Product Manager | Blue | `var(--accent-2)` = `#287be8` |
| Developer | Mint green | `var(--accent)` = `#6ff2c1` |
| QA | Amber | `var(--amber)` = `#f0a500` |
| DevOps | Pink | `var(--pink)` = `#d1458b` |
| Writer | Mint green | `#6ff2c1` |
| Designer | Pink | `#d1458b` |
| Web Publisher | Orange | `var(--orange)` = `#e8682b` |
| Email Marketer | Blue | `var(--accent-2)` = `#287be8` |

---

## Usage Rule

Every HTML file produced for this repo must import Google Fonts as above and
declare all `:root` variables in the `<style>` block. Do not use inline colours
that duplicate a variable — reference the variable instead.
