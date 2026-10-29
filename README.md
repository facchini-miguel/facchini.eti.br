# www.facchini.eti.br

The website of Miguel Facchini's open-source systems: one card per system on the home
page, and a page for each one with its screens and links. Portuguese at the root, English
under `/en/`.

- **Content:** everything is in [`sistemas.yaml`](sistemas.yaml). To add a system, add an
  item there and its screenshots under `estatico/imagens/<id>/`.
- **Build:** `pip install -r requirements.txt && python construir.py` (into `_site/`).
- **Publishing:** GitHub Actions builds and publishes on GitHub Pages on every push, and
  daily, so each system shows its newest GitHub release.
