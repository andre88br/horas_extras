function acompanharTarefa(statusUrl, resultadoUrl) {
    var barra = document.getElementById('tarefa-progress-bar');
    var mensagem = document.getElementById('tarefa-mensagem');

    var intervalo = setInterval(function () {
        fetch(statusUrl)
            .then(function (resposta) { return resposta.json(); })
            .then(function (dados) {
                barra.style.width = dados.percentual + '%';
                barra.setAttribute('aria-valuenow', dados.percentual);
                barra.textContent = dados.percentual + '%';
                if (dados.mensagem) {
                    mensagem.textContent = dados.mensagem;
                }
                if (dados.pronto) {
                    clearInterval(intervalo);
                    window.location.href = resultadoUrl;
                }
            })
            .catch(function () {
                clearInterval(intervalo);
            });
    }, 1000);
}
