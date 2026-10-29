"""Builds the website into _site/ from sistemas.yaml and the templates in modelos/.

Portuguese at the root, Spanish under /es/ and English under /en/. Every link is relative, so the site works at
www.facchini.eti.br and in the GitHub Pages preview address alike.

    pip install -r requirements.txt && python construir.py
"""

import datetime
import hashlib
import json
import shutil
import urllib.request
from pathlib import Path

import qrcode
import qrcode.image.svg
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

RAIZ = Path(__file__).parent
SAIDA = RAIZ / "_site"
IDIOMAS = {"pt": "", "es": "es/", "en": "en/"}
# Brand icons from Simple Icons (CC0), drawn inline in these colors.
MARCAS = {"email": "currentColor", "github": "currentColor", "linkedin": "#0A66C2", "youtube": "#FF0000", "kofi": "#FF5E5B", "pix": "#32BCAD"}

TEXTOS = {
    "pt": {
        "lang": "pt-BR",
        "chamada": "Sistemas de código aberto, gratuitos, para o dia a dia de quem trabalha.",
        "sistemas": "Sistemas",
        "lema": "Sistemas de código aberto",
        "sobre": "Sobre",
        "topicos": "Alguns temas",
        "inscrever": "Inscrever-se no canal",
        "todos_videos": "Todos os vídeos",
        "videos_recentes": "Vídeos recentes",
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
        "pix_qr": "Aponte a câmera do aplicativo do banco",
        "pix_copia": "Pix copia e cola",
        "copiar_chave": "Copiar chave",
        "copiar_codigo": "Copiar código Pix",
        "copiado": "Copiado ✓",
        "sponsors": "GitHub Sponsors",
        "kofi": "Ko-fi",
        "sponsors_texto": "Apoio mensal ou único, com cartão, pelo GitHub.",
        "sponsors_botao": "Patrocinar",
        "kofi_texto": "Uma doação única, com cartão ou PayPal.",
        "kofi_botao": "Pagar um café",
        "voltar": "Todos os sistemas",
        "rodape": "Código aberto, feito no Brasil.",
        "nome_idioma": "Português",
        "dados_ficticios": "As telas mostram apenas dados fictícios.",
        "dica_galeria": "Clique numa tela para ampliar; as setas do teclado ou a roda do mouse passam para a próxima.",
        "anterior": "Tela anterior",
        "proxima": "Próxima tela",
        "fechar": "Fechar",
        "perfis": "Perfis de acesso",
        "tela_inicial_de": "Tela inicial do perfil",
        "perfis_texto": "Cada pessoa da clínica entra com o próprio usuário e senha, e vê só o que o perfil dela permite.",
        "pode": "Pode",
        "nao_pode": "Não pode",
    },
    "es": {
        "lang": "es",
        "chamada": "Sistemas de código abierto, gratuitos, para el día a día de quien trabaja.",
        "sistemas": "Sistemas",
        "lema": "Sistemas de código abierto",
        "sobre": "Sobre mí",
        "topicos": "Algunos temas",
        "inscrever": "Suscribirse al canal",
        "todos_videos": "Todos los videos",
        "videos_recentes": "Videos recientes",
        "apoiar": "Apoyar",
        "versao": "versión",
        "demo": "Demostración",
        "documentacao": "Documentación",
        "codigo": "Código en GitHub",
        "versoes": "Novedades",
        "app": "Aplicación",
        "app_em_breve": "Aplicación: próximamente",
        "saiba_mais": "Saber más",
        "recursos": "Qué hace",
        "telas": "Pantallas",
        "tecnologias": "Hecho con",
        "apoio_texto": "Los sistemas son gratuitos. Si le ayudan, considere apoyar su desarrollo.",
        "apoio_em_breve": "Las formas de apoyo están llegando.",
        "pix": "Pix (Brasil)",
        "pix_chave": "Clave Pix",
        "pix_qr": "Escanee con una aplicación bancaria brasileña",
        "pix_copia": "Pix copiar y pegar",
        "copiar_chave": "Copiar clave",
        "copiar_codigo": "Copiar código Pix",
        "copiado": "Copiado ✓",
        "sponsors": "GitHub Sponsors",
        "kofi": "Ko-fi",
        "sponsors_texto": "Apoyo mensual o único, con tarjeta, a través de GitHub.",
        "sponsors_botao": "Patrocinar",
        "kofi_texto": "Una donación única, con tarjeta o PayPal.",
        "kofi_botao": "Invitar un café",
        "voltar": "Todos los sistemas",
        "rodape": "Código abierto, hecho en Brasil.",
        "nome_idioma": "Español",
        "dados_ficticios": "Las pantallas muestran solo datos ficticios.",
        "dica_galeria": "Haga clic en una pantalla para ampliarla; las flechas del teclado o la rueda del ratón pasan a la siguiente.",
        "anterior": "Pantalla anterior",
        "proxima": "Pantalla siguiente",
        "fechar": "Cerrar",
        "perfis": "Perfiles de acceso",
        "tela_inicial_de": "Pantalla de inicio del perfil",
        "perfis_texto": "Cada persona de la clínica entra con su propio usuario y contraseña, y ve solo lo que su perfil permite.",
        "pode": "Puede",
        "nao_pode": "No puede",
    },
    "en": {
        "lang": "en",
        "chamada": "Free, open-source systems for people's everyday work.",
        "sistemas": "Systems",
        "lema": "Open-source systems",
        "sobre": "About",
        "topicos": "Some topics",
        "inscrever": "Subscribe to the channel",
        "todos_videos": "All videos",
        "videos_recentes": "Recent videos",
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
        "pix_qr": "Scan with a Brazilian bank app",
        "pix_copia": "Pix copy and paste",
        "copiar_chave": "Copy key",
        "copiar_codigo": "Copy Pix code",
        "copiado": "Copied ✓",
        "sponsors": "GitHub Sponsors",
        "kofi": "Ko-fi",
        "sponsors_texto": "Monthly or one-time support, by card, through GitHub.",
        "sponsors_botao": "Sponsor",
        "kofi_texto": "A one-time donation, by card or PayPal.",
        "kofi_botao": "Buy me a coffee",
        "voltar": "All systems",
        "rodape": "Open source, made in Brazil.",
        "nome_idioma": "English",
        "dados_ficticios": "The screens show fake data only.",
        "dica_galeria": "Click a screen to enlarge it; the arrow keys or the mouse wheel move to the next one.",
        "anterior": "Previous screen",
        "proxima": "Next screen",
        "fechar": "Close",
        "perfis": "Access roles",
        "tela_inicial_de": "Home screen of the role",
        "perfis_texto": "Everyone at the clinic signs in with their own username and password, and sees only what their role allows.",
        "pode": "Can",
        "nao_pode": "Cannot",
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


def _campo(codigo, valor):
    return f"{codigo}{len(valor):02d}{valor}"


def _crc16(texto):
    """CRC16-CCITT (polynomial 0x1021, start 0xFFFF), as the BR Code standard asks."""
    crc = 0xFFFF
    for byte in texto.encode():
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) if crc & 0x8000 else crc << 1
            crc &= 0xFFFF
    return f"{crc:04X}"


def pix_copia_e_cola(chave, nome, cidade):
    """Static Pix payload (BR Code, no amount: the donor chooses it in the bank app)."""
    conta = _campo("00", "br.gov.bcb.pix") + _campo("01", chave)
    texto = (
        _campo("00", "01")
        + _campo("26", conta)
        + _campo("52", "0000")
        + _campo("53", "986")
        + _campo("58", "BR")
        + _campo("59", nome[:25])
        + _campo("60", cidade[:15])
        + _campo("62", _campo("05", "***"))
        + "6304"
    )
    return texto + _crc16(texto)


def qr_svg(texto):
    imagem = qrcode.make(texto, image_factory=qrcode.image.svg.SvgPathImage, border=2)
    return imagem.to_string(encoding="unicode")


def marca_svg(nome, cor):
    svg = (RAIZ / "estatico" / "imagens" / "marcas" / f"{nome}.svg").read_text(encoding="utf-8")
    # The size is also on the tag, so an old cached stylesheet never blows it up.
    svg = svg.replace('role="img" ', 'aria-hidden="true" class="marca-icone" width="18" height="18" ')
    svg = svg.replace("<path ", f'<path fill="{cor}" ', 1)
    return svg[: svg.index("<title>")] + svg[svg.index("</title>") + 8 :]


def main():
    dados = yaml.safe_load((RAIZ / "sistemas.yaml").read_text(encoding="utf-8"))
    for sistema in dados["sistemas"]:
        sistema["versao"] = versao_mais_nova(sistema["repositorio"])
    apoio = dados["site"]["apoio"]
    if apoio.get("pix"):
        apoio["pix_codigo"] = pix_copia_e_cola(apoio["pix"], apoio["pix_nome"], apoio["pix_cidade"])
        apoio["pix_qr"] = qr_svg(apoio["pix_codigo"])
    ambiente = Environment(
        loader=FileSystemLoader(RAIZ / "modelos"), autoescape=select_autoescape()
    )
    marcas = {nome: marca_svg(nome, cor) for nome, cor in MARCAS.items()}
    # Changes whenever the CSS or JavaScript changes, so browsers fetch the new files.
    resumo = hashlib.sha256()
    for arquivo in sorted((RAIZ / "estatico").glob("*/*.*")):
        if arquivo.suffix in (".css", ".js"):
            resumo.update(arquivo.read_bytes())
    versao_arquivos = resumo.hexdigest()[:10]
    if SAIDA.exists():
        shutil.rmtree(SAIDA)
    shutil.copytree(RAIZ / "estatico", SAIDA)
    for idioma, pasta in IDIOMAS.items():
        paginas = [("index.html", "inicio.html", None), ("sobre/index.html", "sobre.html", None)] + [
            (f"{s['id']}/index.html", "sistema.html", s) for s in dados["sistemas"]
        ]
        for destino, modelo, sistema in paginas:
            caminho = pasta + destino
            profundidade = caminho.count("/")
            raiz = "../" * profundidade or "./"
            pagina = ambiente.get_template(modelo).render(
                site=dados["site"],
                sistemas=dados["sistemas"],
                sobre=dados["sobre"],
                sistema=sistema,
                idioma=idioma,
                t=TEXTOS[idioma],
                raiz=raiz,
                prefixo=pasta,
                marcas=marcas,
                versao_arquivos=versao_arquivos,
                ano=datetime.date.today().year,
                # The same page in each language, for the flags in the header.
                idiomas=[
                    {
                        "codigo": codigo,
                        "lang": TEXTOS[codigo]["lang"],
                        "nome": TEXTOS[codigo]["nome_idioma"],
                        "url": raiz + IDIOMAS[codigo] + destino.removesuffix("index.html"),
                    }
                    for codigo in IDIOMAS
                ],
            )
            arquivo = SAIDA / caminho
            arquivo.parent.mkdir(parents=True, exist_ok=True)
            arquivo.write_text(pagina, encoding="utf-8")
    (SAIDA / ".nojekyll").write_text("")
    print(f"Site pronto em {SAIDA}")


if __name__ == "__main__":
    main()
