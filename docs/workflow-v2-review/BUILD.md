# Rebuild the reference deck

The editable source is process.qmd with slides.scss. Render the standalone HTML:

    quarto render process.qmd --to revealjs

Open process.html in Chrome. Use the presentation's PDF/print view, allow the slides to finish loading, then print to PDF with background graphics enabled and browser headers/footers disabled. Save as process.pdf.

The supplied PDF is the browser print rendering of the Quarto HTML, not a separate PowerPoint or unrelated document. It has 15 landscape pages. Wait for Reveal to initialize before printing: printing immediately during page load can produce a blank one-page file.

For offline review-prototype contract checks:

    python3 -B -m unittest discover -s . -p 'test_*.py'

progress.html is self-contained and includes synthetic scenarios; it works when opened directly without a server. It is a review demonstration, not a production monitor, source adapter, notification service or authenticated approval system.

Patrick approved the design, write profile and checkpoint times on 10 November 2026. Current installation/publication and pilot status are recorded in ../workflow-v2-implementation.md. Keep generated caches and all private run/approval data outside the public package.

For the operational runner, from the repository root:

    python3 -B -m unittest discover -s tools/race_v2 -p 'test_*.py'

Its private run viewer is generated from actual checksummed state. The public progress.html remains a synthetic reference demonstration.
