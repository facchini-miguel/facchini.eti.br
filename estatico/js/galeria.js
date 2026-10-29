// Screenshot viewer: a click on a screenshot opens it large; the arrow keys, the
// buttons, the mouse wheel, a click on either half of the image or a swipe move
// to the previous or next one. Without JavaScript each link opens the image itself.
(function () {
  const lista = document.querySelector(".telas");
  if (!lista || !window.HTMLDialogElement) return;
  const telas = [...lista.querySelectorAll("figure")].map((figura) => ({
    src: figura.querySelector("a").href,
    legenda: figura.querySelector("figcaption").textContent,
  }));
  const r = lista.dataset;

  const dialogo = document.createElement("dialog");
  dialogo.className = "galeria";
  dialogo.innerHTML = `
    <button type="button" class="galeria-fechar" aria-label="${r.fechar}">×</button>
    <button type="button" class="galeria-seta galeria-anterior" aria-label="${r.anterior}">‹</button>
    <figure><img alt=""><figcaption><span class="galeria-legenda"></span><span class="galeria-posicao"></span></figcaption></figure>
    <button type="button" class="galeria-seta galeria-proxima" aria-label="${r.proxima}">›</button>`;
  document.body.append(dialogo);
  const imagem = dialogo.querySelector("img");
  let atual = 0;

  function mostrar(indice) {
    atual = (indice + telas.length) % telas.length;
    imagem.src = telas[atual].src;
    imagem.alt = telas[atual].legenda;
    dialogo.querySelector(".galeria-legenda").textContent = telas[atual].legenda;
    dialogo.querySelector(".galeria-posicao").textContent = `${atual + 1} / ${telas.length}`;
    // Load the next one ahead, so moving forward is instant.
    new Image().src = telas[(atual + 1) % telas.length].src;
  }

  lista.querySelectorAll("figure a").forEach((link, indice) => {
    link.addEventListener("click", (evento) => {
      evento.preventDefault();
      mostrar(indice);
      dialogo.showModal();
    });
  });

  dialogo.querySelector(".galeria-fechar").addEventListener("click", () => dialogo.close());
  dialogo.querySelector(".galeria-anterior").addEventListener("click", () => mostrar(atual - 1));
  dialogo.querySelector(".galeria-proxima").addEventListener("click", () => mostrar(atual + 1));
  // A click on the image: left half goes back, right half goes forward.
  imagem.addEventListener("click", (evento) => {
    const caixa = imagem.getBoundingClientRect();
    mostrar(evento.clientX < caixa.left + caixa.width / 2 ? atual - 1 : atual + 1);
  });
  // A click on the dark backdrop closes.
  dialogo.addEventListener("click", (evento) => {
    if (evento.target === dialogo) dialogo.close();
  });

  dialogo.addEventListener("keydown", (evento) => {
    const passos = { ArrowRight: 1, ArrowDown: 1, PageDown: 1, " ": 1, ArrowLeft: -1, ArrowUp: -1, PageUp: -1 };
    if (evento.key in passos) mostrar(atual + passos[evento.key]);
    else if (evento.key === "Home") mostrar(0);
    else if (evento.key === "End") mostrar(telas.length - 1);
    else return;
    evento.preventDefault();
  });

  // One step per wheel gesture: a touchpad sends many small events.
  let rodaParada = true;
  dialogo.addEventListener("wheel", (evento) => {
    evento.preventDefault();
    if (!rodaParada || Math.abs(evento.deltaY) + Math.abs(evento.deltaX) < 4) return;
    rodaParada = false;
    mostrar(atual + (evento.deltaY + evento.deltaX > 0 ? 1 : -1));
    setTimeout(() => (rodaParada = true), 350);
  }, { passive: false });

  let toqueX = null;
  dialogo.addEventListener("touchstart", (evento) => (toqueX = evento.touches[0].clientX), { passive: true });
  dialogo.addEventListener("touchend", (evento) => {
    if (toqueX === null) return;
    const distancia = evento.changedTouches[0].clientX - toqueX;
    if (Math.abs(distancia) > 40) mostrar(atual + (distancia < 0 ? 1 : -1));
    toqueX = null;
  });
})();
