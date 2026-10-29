"""Builds the website into _site/ from sistemas.yaml and the templates in modelos/.

Portuguese at the root, English under /en/. Every link is relative, so the site works at
www.facchini.eti.br and in the GitHub Pages preview address alike.

    pip install -r requirements.txt && python construir.py
"""

import json
import shutil
import urllib.request
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

RAIZ = Path(__file__).parent
SAIDA = RAIZ / "_site"
IDIOMAS = {"pt": "", "en": "en/"}

TEXTOS = {
    "pt": {
        "lang": "pt-BR",
        "chamada": "Sistemas de código aberto, gratuitos, para o dia a dia de quem trabalha.",
        "sistemas": "Sistemas",
        "apoiar": "Apoiar",
        "versao": "versão",
        "demo": "Demonstração",
        "documentacao": "Documentação",
        "codigo": "Código no GitHub",
        "versoes": "Novidades",
        "app": "Aplicativo",
        "app_em_breve": "Aplicativo: em breve",
        "saiba_mais": "Saiba mais",
        "recursos": "O que faz",
        "telas": "Telas",
        "tecnologias": "Feito com",
        "apoio_texto": "Os sistemas são gratuitos. Se eles ajudam você, considere apoiar o desenvolvimento.",
        "apoio_em_breve": "As formas de apoio estão chegando.",
        "pix": "Pix",
        "pix_chave": "Chave Pix",
        "sponsors": "GitHub Sponsors",
        "kofi": "Ko-fi",
        "voltar": "Todos os sistemas",
        "rodape": "Código aberto, feito no Brasil.",
        "outro_idioma": "English",
        "dados_ficticios": "As telas mostram apenas dados fictícios.",
    },
    "en": {
        "lang": "en",
        "chamada": "Free, open-source systems for people's everyday work.",
        "sistemas": "Systems",
        "apoiar": "Support",
        "versao": "version",
        "demo": "Demo",
        "documentacao": "Documentation",
        "codigo": "Code on GitHub",
        "versoes": "Releases",
        "app": "App",
        "app_em_breve": "App: coming soon",
        "saiba_mais": "Learn more",
        "recursos": "What it does",
        "telas": "Screens",
        "tecnologias": "Built with",
        "apoio_texto": "The systems are free. If they help you, consider supporting their development.",
        "apoio_em_breve": "Ways to support are coming soon.",
        "pix": "Pix (Brazil)",
        "pix_chave": "Pix key",
        "sponsors": "GitHub Sponsors",
        "kofi": "Ko-fi",
        "voltar": "All systems",
        "rodape": "Open source, made in Brazil.",
        "outro_idioma": "Português",
        "dados_ficticios": "The screens show fake data only.",
    },
}


def versao_mais_nova(repositorio):
    """Tag of the newest GitHub release, or None when GitHub cannot be reached."""
    url = f"https://api.github.com/repos/{repositorio}/releases/latest"
    try:
        with urllib.request.urlopen(url, timeout=10) as resposta:
            return json.load(resposta)["tag_name"].lstrip("v")
    except Exception:  # noqa: BLE001 - the site is still built without the version
        return None


def main():
    dados = yaml.safe_load((RAIZ / "sistemas.yaml").read_text(encoding="utf-8"))
    for sistema in dados["sistemas"]:
        sistema["versao"] = versao_mais_nova(sistema["repositorio"])
    ambiente = Environment(
        loader=FileSystemLoader(RAIZ / "modelos"), autoescape=select_autoescape()
    )
    if SAIDA.exists():
        shutil.rmtree(SAIDA)
    shutil.copytree(RAIZ / "estatico", SAIDA)
    for idioma, pasta in IDIOMAS.items():
        outro = "en" if idioma == "pt" else "pt"
        paginas = [("index.html", "inicio.html", None)] + [
            (f"{s['id']}/index.html", "sistema.html", s) for s in dados["sistemas"]
        ]
        for destino, modelo, sistema in paginas:
            caminho = pasta + destino
            profundidade = caminho.count("/")
            raiz = "../" * profundidade or "./"
            pagina = ambiente.get_template(modelo).render(
                site=dados["site"],
                sistemas=dados["sistemas"],
                sistema=sistema,
                idioma=idioma,
                t=TEXTOS[idioma],
                raiz=raiz,
                # The same page in the other language.
                outro_idioma=raiz + IDIOMAS[outro] + destino.removesuffix("index.html"),
            )
            arquivo = SAIDA / caminho
            arquivo.parent.mkdir(parents=True, exist_ok=True)
            arquivo.write_text(pagina, encoding="utf-8")
    (SAIDA / ".nojekyll").write_text("")
    print(f"Site pronto em {SAIDA}")


if __name__ == "__main__":
    main()
