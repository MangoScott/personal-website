# Scott Glasgow - Personal Website

Personal site for Scott Glasgow, served by GitHub Pages at [sglasgow.com](https://sglasgow.com). Plain HTML/CSS/JS. No build step, no dependencies.

## Pages

- **index.html** - Homepage with an interactive physics hero (draggable balls linking to projects), about blurb, education, and contact
- **about.html** - Personal story, from Akron to 39 countries
- **projects.html** - Project cards (Fresho, FinMango, Raging Robot Radio, and archived work)
- **publications.html** - Peer-reviewed papers, op-eds, books, media mentions, TEDx talks, podcasts
- **travel.html** - Masonry photo gallery with lightbox, fed by WebP thumbnails
- **speaking.html** - TEDx video, speaking topics, and past venues
- **404.html** - Not-found page (picked up automatically by GitHub Pages)

## Structure

- **styles.css** - Shared design system (CSS variables, header/nav, cards, gallery, lightbox). `index.html` carries its own inline styles for the physics hero.
- **js/main.js** - Shared mobile menu toggle used by every page
- **images/** - Page images. `images/travel/` holds full-size gallery photos (used by the lightbox); `images/travel/thumbs/` holds 800px WebP thumbnails (used by the grid).
- **sitemap.xml / robots.txt** - Search engine plumbing; URLs point at https://sglasgow.com

## Conventions

- The canonical domain is **sglasgow.com** (see CNAME). Keep `og:url`, `twitter:url`, and `link rel="canonical"` tags on that domain.
- Strip EXIF metadata (especially GPS) from any photo before committing it. Any Pillow/ImageMagick re-save without metadata works.
- New travel photos need both a full-size JPEG in `images/travel/` and an 800px-wide WebP in `images/travel/thumbs/`, plus `width`/`height` attributes on the `<img>` tag.
- Mark the current page in the nav with `class="active"`.

## Deployment

Push to `main`. GitHub Pages serves the repository root; the custom domain is configured via the `CNAME` file.

---

Built with intention. © 2026 Scott Glasgow
