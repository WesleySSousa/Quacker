const form = document.getElementById("downloadForm");
const input = document.getElementById("videoInput");
const mensagem = document.getElementById("mensagem");

const validLinks = [
  // YouTube: watch, youtu.be, shorts
  /(https?:\/\/)?(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/shorts\/)[\w-]+/i,

  // TikTok: links normais e encurtados (vt.tiktok.com)
  /(https?:\/\/)?(www\.)?(tiktok\.com\/.+|vt\.tiktok\.com\/[\w-]+)/i,

  // Instagram
  /(https?:\/\/)?(www\.)?instagram\.com\/.+/i,

  // Facebook
  /(https?:\/\/)?(www\.)?facebook\.com\/.+/i,

  // Twitch
  /(https?:\/\/)?(www\.)?twitch\.tv\/.+/i,
];

function validarLink(url) {
  return validLinks.some((regex) => regex.test(url));
}

form.addEventListener("submit", async (e) => {
  e.preventDefault(); // evita recarregar a página

  const url = input.value.trim();

  if (!validarLink(url)) {
    mensagem.style.display = "block";
    mensagem.textContent = "Cole um link válido.";
    return;
  }

  // Mostra mensagem de download
  mensagem.style.display = "block";
  mensagem.textContent = "Preparando download...";

  try {
    // Envia o link via AJAX
    const response = await fetch("/download", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: `video_url=${encodeURIComponent(url)}`,
    });

    // Se o download for um arquivo, baixamos
    if (response.ok) {
      const blob = await response.blob();
      const a = document.createElement("a");
      const filename = url.split("/").pop() + ".mp4"; // nome simples
      a.href = window.URL.createObjectURL(blob);
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();

      mensagem.textContent = "Download concluído!";
      input.value = ""; // limpa apenas após concluir
    } else {
      const text = await response.text();
      mensagem.textContent = "Erro: " + text;
    }
  } catch (err) {
    mensagem.textContent = "Erro ao processar o download.";
    console.error(err);
  }
});
