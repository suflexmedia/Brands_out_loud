---
trigger: always_on
---

We are ready to build the next page for our BOL (Brands Out Loud) FastAPI-based web application.

Here are the details for the page we are implementing:

- **Page Name:** Magazine Page Remaster
- **Target HTML Filename:** page_serving_routers/static/templates/magazine_remaster.html
- **Target CSS Filename:** page_serving_routers/static/css/magazine_remaster.css
- **Figma CSS Reference File:** page_serving_routers/static/templates/figma_reference/figma.css
- **Figma Visual Design Reference:** page_serving_routers/static/templates/figma_reference/image.png
- **Page Route:** /magazine_remaster

Please adhere strictly to our established project architecture and coding guidelines:

### 1. Structure & Navigation Consistency

- Re-use the exact same Navbar and Footer structures established in `page_serving_routers/static/templates/homepage_remaster.html`.
- Use `{% include 'partials/navbar.html' %}` for the header, and copy the footer implementation from `homepage_remaster.html`.
- Ensure all links in the header and footer navigate to their correct FastAPI routes.

### 2. Sizing, Spacing & Layout

- Use viewport units (`vw` and `vh`) for major spacing, section padding, margins, and key element dimensions so the design scales fluidly. Avoid `px` and `rem` where possible as they might break with screen sizes.
- Convert absolute pixel coordinates from the Figma CSS (`figma.css`) and visual reference (`image.png`) to responsive flexbox/grid containers.
- Build section by section. Focus on creating and refining each section before moving to the next.
- Focus on creating and refining the mobile design. Ensure any changes, including media queries and mobile CSS, do not hamper or break the existing desktop implementation.

### 3. SVG & Logo Handling

- Do NOT embed raw `<svg>` tags or inline SVG code directly in the HTML (unless already present in standard partials).
- For new vector elements or icons, save them as separate `.svg` files in the `static/images/` directory and reference them via `<img>` tags.

### 4. Image Placeholders

- Do not use locally generated placeholder images.
- Use the Picsum API (e.g., `https://picsum.photos/800/600?random=seed_name`) directly for all page illustrations and photography slots.

### 5. Strict Coding Rules (Non-Negotiable)

- **Zero Comments:** Do NOT include any comments (no inline or block comments like `#`, `//`, or `/* */`) in the HTML, CSS, JS, or Python code. Only Python docstrings are permitted where necessary.
- **Windows Commands:** If you run any shell/terminal commands, use `;` instead of `&&` as the command separator.
- **Venv activation:** Activate the existing `venv` virtual environment before executing any Python/dependency actions.

---

## Implementation Plan for Magazine Page Remaster

### Phase 1: Analysis & Setup
- Analyze `homepage_remaster.html` and `homepage_remaster.css` to understand the existing navbar, footer, layout structure, and Jinja templating.
- Map the provided Figma visual design (`image.png`) and Figma CSS (`figma.css`) into modular HTML sections to build section by section.
- Ensure the `/magazine_remaster` route is appropriately registered in the FastAPI app.

### Phase 2: Desktop Layout & Section-by-Section Building
- Create/update the HTML skeleton in `magazine_remaster.html`.
- Update `magazine_remaster.css` and link it in `magazine_remaster.html`.
- Convert Figma's absolute positioning and pixel units into a responsive Flexbox/Grid layout utilizing `vw` and `vh` section by section.
- Re-use the standard Navbar and Footer from `homepage_remaster.html`.
- Integrate dynamic data slots (using Jinja2 syntax) if required by the design, or prepare the structure with static placeholders initially.
- Use Picsum for any new placeholder images.

### Phase 3: Mobile Responsiveness
- Update the mobile design without hampering the desktop version.
- Add media queries and mobile responsiveness, ensuring the desktop implementation remains strictly unaffected.

