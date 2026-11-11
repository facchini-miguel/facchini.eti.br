# www.facchini.eti.br

The website of Miguel Facchini's open-source systems: one card per system on the home
page, and a page for each one with its screens and links. Portuguese at the root, English
under `/en/`.

- **Content:** everything is in [`sistemas.yaml`](sistemas.yaml). To add a system, add an
  item there and its screenshots under `estatico/imagens/<id>/`. Screenshots in English or
  Spanish go in `estatico/imagens/<id>/en/` and `.../es/` with the same file name; the page
  in that language uses them, and falls back to the Portuguese one when a file is missing.
- **Build:** `pip install -r requirements.txt && python construir.py` (into `_site/`).
- **Publishing:** the site runs on the VPS, in Dokploy ([`deploy/`](deploy/)). Its builder
  fetches `main` every 2 minutes and rebuilds the site on every new commit and every 10
  minutes, so each system shows its newest GitHub release; nginx serves it behind Dokploy's
  Traefik, and `facchini.eti.br` redirects to `www.facchini.eti.br`. A merge to `main` is live
  within 2 minutes, with nothing else to run. GitHub Actions only checks that the site builds.
- **Changing the server side** (`deploy/compose.yml`): run `deploy/apply.sh` from your machine
  (it needs `ssh vps`). It creates or updates the Compose in Dokploy, deploys it and checks
  the pages, the redirect and the HTTPS certificates.
