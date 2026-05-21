---
name: designer-ui-ux
description: >-
  Applies accessibility, responsive design, and usability standards to any UI work — ensures the site works for people with disabilities, looks correct on all screen sizes, and has clear interactive states for every button, link, and form. Reference this when reviewing or designing any page component.
---

# Designer: UI/UX Best Practices

- **Accessibility first**: WCAG 2.1 AA minimum, semantic HTML, ARIA labels, sufficient color contrast (4.5:1 text, 3:1 large text)
- **Responsive**: mobile-first, test at 320px, 768px, 1024px, 1440px
- **Performance**: lazy-load images, minimize CLS, use next/image, avoid layout shifts
- **Interaction states**: hover, focus, active, disabled, loading, error — all must be styled
- **Consistency**: same patterns for same problems — one button style, one card style, one form pattern
- **Progressive disclosure**: show what's needed, hide what's not. No information overload
- **Touch targets**: minimum 44x44px for interactive elements on mobile
- **Loading states**: skeleton screens preferred over spinners for content-heavy areas
