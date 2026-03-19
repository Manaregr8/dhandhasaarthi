from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright


def main() -> None:
    here = Path(__file__).resolve().parent
    html_path = here / "dhandhasaarthi-portfolio.html"
    if not html_path.exists():
        raise FileNotFoundError(f"HTML file not found: {html_path}")

    base_output_path = here / "dhandhasaarthi-portfolio.pdf"
    url = html_path.as_uri()

    # When exporting to PDF, CSS animations can freeze at opacity:0 (e.g. `.delay-*`).
    # Override animations so all content is visible.
    no_anim_css = """
    * { animation: none !important; transition: none !important; }
    .fade-up, .delay-1, .delay-2, .delay-3, .delay-4 { opacity: 1 !important; transform: none !important; }
    """

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        page.goto(url, wait_until="load")
        page.add_style_tag(content=no_anim_css)
        page.wait_for_timeout(750)

        output_path = base_output_path
        last_error: Exception | None = None
        for i in range(0, 10):
            candidate = (
                base_output_path
                if i == 0
                else here / f"dhandhasaarthi-portfolio-{i}.pdf"
            )
            try:
                page.pdf(
                    path=str(candidate),
                    format="A4",
                    print_background=True,
                    prefer_css_page_size=True,
                    margin={"top": "12mm", "bottom": "12mm", "left": "10mm", "right": "10mm"},
                )
                output_path = candidate
                last_error = None
                break
            except PermissionError as exc:
                last_error = exc

        if last_error is not None:
            raise last_error
        browser.close()

    print(f"Wrote PDF: {output_path}")


if __name__ == "__main__":
    main()
