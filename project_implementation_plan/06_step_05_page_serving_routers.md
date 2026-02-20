# Step 05: Page Serving Routers

## Objective
Migrate all endpoints that render HTML templates from the monolithic `app.py` into specialized routers under `page_serving_routers/`. Set up static file serving correctly.

## Prerequisites
- Step 02 (Database Handler) completed.
- Jinja2 and Aiofiles installed.
- HTML templates and Static files moved into `page_serving_routers/templates` and `page_serving_routers/static`.

## Implementation Details
1. **Template Config**: In `page_serving_routers/__init__.py` or a core module, instantiate `Jinja2Templates(directory="page_serving_routers/templates")`.
2. **Router Setup**: Create modules like `pages.py`, `admin_pages.py`.
3. **Endpoint Migration Example**:
    - The central route `/<data>` logic needs to be unrolled or cleanly pattern-matched. In FastAPI, `("/{data}")` is valid but care must be taken so it doesn't shadow explicit routes like `/login`. It's recommended to place the catch-all dynamic route at the bottom.
    - Move `index` (`/`), `/login`, `/register`, `/magazine` to `page_serving_routers/pages.py`.
    - Modify the view functions to `return templates.TemplateResponse("template.html", {"request": request, "data": data})`.
4. **Static Mount**: We will mount the static folder in the main `app.py` or within this router namespace, allowing CSS/JS to be loaded correctly via `url_for('static', path='styles.css')`.

## Research Areas
- **Global Context in Jinja2**: Figure out how global functions (like `get_header()`, if they contain logic) map to Jinja2 context processors in FastAPI.
- **HTML forms vs JSON**: Identify if any templates use standard HTML form POSTs rather than JSON/AJAX. If so, those endpoints will need `fastapi.Form`.

## Expected Outcome
- A suite of `APIRouter` instances that specifically handle `GET` requests from browsers and return rendered HTML via Jinja2.

## Estimated Effort
2 Days

## Dependencies
- Depends on: Step 02
- Depended on by: Step 06
