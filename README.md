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
  within 2 minutes, with nothing else to run. GitHub Actions checks that the site builds, and
  lints `construir.py` with ruff (`ruff.toml`: the classic rules, `E4, E7, E9, F`).
- **Changing the server side** (`deploy/compose.yml`): run `deploy/apply.sh` from your machine
  (it needs `ssh vps`). It creates or updates the Compose in Dokploy, deploys it and checks
  the pages, the redirect and the HTTPS certificates.

## Shared workflows of the public repositories

`.github/workflows/reusable-lint.yml` and `reusable-image-age.yml` are copies, for the owner's
public repositories (Kaladrius, this one), of the shared workflows of facchini-miguel/arauto,
which is private: a public repository cannot call a private one's workflows. The owner decided
it: "coloca o que o ci faz no facchini.eti.br, ele fica para os publicos ... e para o privado,
deixa o arauto". Their source is arauto's: a change is made there and brought here by a pull
request, the same from the `name:` line on, and arauto's CI warns while they differ. How they
work and their inputs: arauto's README, "Shared workflows". A caller pins a commit of this
repository: `uses: facchini-miguel/facchini.eti.br/.github/workflows/reusable-lint.yml@<sha>`.
