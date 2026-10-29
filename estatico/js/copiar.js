// "Copy" buttons: copy the text of the element named in data-copiar to the clipboard
// and confirm on the button for a moment.
document.querySelectorAll("button[data-copiar]").forEach((botao) => {
  const texto = botao.textContent;
  botao.addEventListener("click", async () => {
    const valor = document.getElementById(botao.dataset.copiar).textContent.trim();
    try {
      await navigator.clipboard.writeText(valor);
    } catch {
      // Older browsers or no permission: select the text so the user can copy it.
      const selecao = window.getSelection();
      selecao.selectAllChildren(document.getElementById(botao.dataset.copiar));
      document.execCommand("copy");
    }
    botao.textContent = botao.dataset.copiado;
    botao.classList.add("copiado");
    setTimeout(() => {
      botao.textContent = texto;
      botao.classList.remove("copiado");
    }, 2000);
  });
});
