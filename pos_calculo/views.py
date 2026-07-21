from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse

from pos_calculo.credenciais import preparar_selenium
from pos_calculo.processamento import rejeita_todos, rejeita_especifico, inicia_driver, \
    clica_frequencia, recalcula_todos, recalcula_especifico, lanca_todos, lanca_especifico, voltar_todos, \
    recalcula_negativos, clica_horario_excepcional
from pos_calculo.tirar_escala import tirar_escala
from pos_calculo.voltar_negativos import voltar_escala
from tarefas.executor import iniciar_tarefa

_LOCK_SELENIUM = 'pos_calculo_selenium'


def exige_sigp(view):
    """Garante que a pessoa informou o login do SIGP (guardado na sessão).

    Sem credenciais na sessão, redireciona para a tela de login do SIGP,
    retornando depois para a ação original (parâmetro ?next=).
    """
    @wraps(view)
    def _wrapper(request, *args, **kwargs):
        if not request.session.get('sigp_usuario'):
            return redirect(f"{reverse('login_sigp')}?next={request.path}")
        return view(request, *args, **kwargs)
    return _wrapper


def _credenciais_sessao(request):
    return request.session.get('sigp_usuario'), request.session.get('sigp_senha')


def login_sigp(request):
    """Coleta usuário/senha do SIGP e guarda na sessão do navegador da pessoa.

    Cada pessoa usa o próprio login do SIGP; ele é informado uma vez por sessão
    e reaproveitado por todas as ações do pos_calculo.
    """
    proximo = request.GET.get('next') or request.POST.get('next') or reverse('rejeitar_batidas')
    if request.method == "POST":
        usuario = request.POST.get('sigp_usuario', '').strip()
        senha = request.POST.get('sigp_senha', '')
        if usuario and senha:
            request.session['sigp_usuario'] = usuario
            request.session['sigp_senha'] = senha
            return redirect(proximo)
        messages.error(request, 'Informe usuário e senha do SIGP.')
    return render(request, "pos_calculo/login_sigp.html",
                  {'next': proximo, 'sigp_usuario': request.session.get('sigp_usuario', '')})


def logout_sigp(request):
    request.session.pop('sigp_usuario', None)
    request.session.pop('sigp_senha', None)
    messages.info(request, 'Você saiu do SIGP.')
    return redirect('login_sigp')


@exige_sigp
def rejeitar_batidas(request):
    if request.method == "POST":
        data = request.POST.get('data')
        mes = int(str(data).split('-')[1])
        ano = int(str(data).split('-')[0])
        matricula = request.POST.get('matricula')
        usuario = request.user
        sigp = _credenciais_sessao(request)

        def worker(progress_callback):
            preparar_selenium(*sigp, progress_callback)
            progress_callback(10, 'Iniciando navegador...')
            driver = inicia_driver()
            try:
                clica_frequencia(driver)
                progress_callback(30, 'Rejeitando batidas...')
                c = 0
                if matricula == '':
                    rejeita_todos(mes, ano, driver, c, usuario)
                else:
                    rejeita_especifico(mes, ano, driver, c, matricula, usuario)
                return {'mensagem': 'Batidas rejeitadas com sucesso', 'nivel': 'success'}
            finally:
                driver.quit()

        tarefa = iniciar_tarefa(tipo='pos_calculo.rejeitar_batidas', usuario=usuario,
                                template_resultado='pos_calculo/rejeitar_batidas.html', func=worker,
                                lock_key=_LOCK_SELENIUM)
        return redirect('tarefa_acompanhar', tarefa_id=tarefa.id)
    return render(request, "pos_calculo/rejeitar_batidas.html")


@exige_sigp
def recalcular_banco(request):
    if request.method == "POST":
        data = request.POST.get('data')
        mes = int(str(data).split('-')[1])
        ano = int(str(data).split('-')[0])
        matricula = request.POST.get('matricula')
        processo = request.POST.get('processo')
        usuario = request.user
        sigp = _credenciais_sessao(request)

        def worker(progress_callback):
            preparar_selenium(*sigp, progress_callback)
            progress_callback(10, 'Iniciando navegador...')
            if matricula == '':
                resposta = recalcula_todos(mes, ano, processo, usuario)
            else:
                resposta = recalcula_especifico(mes, ano, matricula, processo, usuario)
            mes_exibido = f'0{mes}' if mes < 10 else mes
            if resposta == 'ok':
                return {'mensagem': 'Bancos calculados com sucesso', 'nivel': 'success'}
            return {'mensagem': f'Matrícula não localizada na confirmação de horas extras do mês de '
                                f'{mes_exibido}/{ano}', 'nivel': 'error'}

        tarefa = iniciar_tarefa(tipo='pos_calculo.recalcular_banco', usuario=usuario,
                                template_resultado='pos_calculo/recalcular_banco.html', func=worker,
                                lock_key=_LOCK_SELENIUM)
        return redirect('tarefa_acompanhar', tarefa_id=tarefa.id)
    return render(request, "pos_calculo/recalcular_banco.html")


@exige_sigp
def pagamento(request):
    if request.method == "POST":
        data = request.POST.get('data')
        mes = int(str(data).split('-')[1])
        ano = int(str(data).split('-')[0])
        data_folha = request.POST.get('data_folha')
        mes_folha = int(str(data_folha).split('-')[1])
        ano_folha = int(str(data_folha).split('-')[0])
        matricula = request.POST.get('matricula')
        fator = request.POST.get('fator')
        processo = request.POST.get('processo')
        usuario = request.user
        sigp = _credenciais_sessao(request)

        if mes_folha < 10:
            mes_folha = f'0{mes_folha}'

        def worker(progress_callback):
            preparar_selenium(*sigp, progress_callback)
            progress_callback(10, 'Iniciando navegador...')
            if matricula == '':
                resposta = lanca_todos(mes, ano, mes_folha, ano_folha, fator, processo, usuario)
            else:
                resposta = lanca_especifico(mes, ano, mes_folha, ano_folha, matricula, fator, processo, usuario)
            mes_exibido = f'0{mes}' if mes < 10 else mes
            if resposta == 'ok':
                return {'mensagem': 'Rubricas lançadas com sucesso', 'nivel': 'success'}
            return {'mensagem': f'Matrícula não localizada na confirmação de horas extras do mês de '
                                f'{mes_exibido}/{ano}', 'nivel': 'error'}

        tarefa = iniciar_tarefa(tipo='pos_calculo.pagamento', usuario=usuario,
                                template_resultado='pos_calculo/pagamento.html', func=worker,
                                lock_key=_LOCK_SELENIUM)
        return redirect('tarefa_acompanhar', tarefa_id=tarefa.id)
    return render(request, "pos_calculo/pagamento.html")


@exige_sigp
def voltar_batidas(request):
    if request.method == "POST":
        data = request.POST.get('data')
        mes = int(str(data).split('-')[1])
        ano = int(str(data).split('-')[0])
        usuario = request.user
        sigp = _credenciais_sessao(request)

        def worker(progress_callback):
            preparar_selenium(*sigp, progress_callback)
            progress_callback(10, 'Iniciando navegador...')
            driver = inicia_driver()
            try:
                clica_frequencia(driver)
                progress_callback(30, 'Desrejeitando batidas...')
                c = 0
                voltar_todos(mes, ano, driver, c, usuario)
                return {'mensagem': 'Batidas desrejeitadas com sucesso', 'nivel': 'success'}
            finally:
                driver.quit()

        tarefa = iniciar_tarefa(tipo='pos_calculo.voltar_batidas', usuario=usuario,
                                template_resultado='pos_calculo/voltar_batidas.html', func=worker,
                                lock_key=_LOCK_SELENIUM)
        return redirect('tarefa_acompanhar', tarefa_id=tarefa.id)
    return render(request, "pos_calculo/voltar_batidas.html")


@exige_sigp
def voltar_escalas(request):
    if request.method == "POST":
        data = request.POST.get('data')
        mes = int(str(data).split('-')[1])
        ano = int(str(data).split('-')[0])
        usuario = request.user
        sigp = _credenciais_sessao(request)

        def worker(progress_callback):
            preparar_selenium(*sigp, progress_callback)
            progress_callback(10, 'Iniciando navegador...')
            driver = inicia_driver()
            try:
                clica_horario_excepcional(driver)
                progress_callback(30, 'Incluindo escalas...')
                c = 0
                try:
                    voltar_escala(mes, ano, driver, c, usuario)
                except Exception as error:
                    if str(error) == "'matricula'":
                        return {'mensagem': f'Sem escalas para voltar do mês de {mes}/{ano}', 'nivel': 'error'}
                    raise
                return {'mensagem': 'Escalas incluídas com sucesso', 'nivel': 'success'}
            finally:
                driver.quit()

        tarefa = iniciar_tarefa(tipo='pos_calculo.voltar_escalas', usuario=usuario,
                                template_resultado='pos_calculo/voltar_escalas.html', func=worker,
                                lock_key=_LOCK_SELENIUM)
        return redirect('tarefa_acompanhar', tarefa_id=tarefa.id)
    return render(request, "pos_calculo/voltar_escalas.html")


@exige_sigp
def recalcular_negativos(request):
    if request.method == "POST":
        data = request.POST.get('data')
        mes = int(str(data).split('-')[1])
        ano = int(str(data).split('-')[0])
        processo = request.POST.get('processo')
        usuario = request.user
        sigp = _credenciais_sessao(request)

        def worker(progress_callback):
            preparar_selenium(*sigp, progress_callback)
            progress_callback(10, 'Iniciando navegador...')
            resposta = recalcula_negativos(mes, ano, processo, usuario)
            mes_exibido = f'0{mes}' if mes < 10 else mes
            if resposta == 'ok':
                return {'mensagem': 'Bancos calculados com sucesso', 'nivel': 'success'}
            if resposta == 'vazio':
                return {'mensagem': f'Nenhum banco negativo na confirmação de {mes_exibido}/{ano} '
                                    f'para recalcular.', 'nivel': 'info'}
            return {'mensagem': f'Matrícula não localizada na confirmação de horas extras do mês de '
                                f'{mes_exibido}/{ano}', 'nivel': 'error'}

        tarefa = iniciar_tarefa(tipo='pos_calculo.recalcular_negativos', usuario=usuario,
                                template_resultado='pos_calculo/recalcular_negativos.html', func=worker,
                                lock_key=_LOCK_SELENIUM)
        return redirect('tarefa_acompanhar', tarefa_id=tarefa.id)
    return render(request, "pos_calculo/recalcular_negativos.html")


@exige_sigp
def excluir_escalas(request):
    if request.method == "POST":
        data = request.POST.get('data')
        mes = int(str(data).split('-')[1])
        ano = int(str(data).split('-')[0])
        usuario = request.user
        sigp = _credenciais_sessao(request)

        def worker(progress_callback):
            preparar_selenium(*sigp, progress_callback)
            progress_callback(10, 'Iniciando navegador...')
            driver = inicia_driver()
            try:
                clica_horario_excepcional(driver)
                progress_callback(30, 'Excluindo escalas...')
                c = 0
                try:
                    tirar_escala(mes, ano, driver, c, usuario)
                except Exception as error:
                    if str(error) == "'matricula'":
                        return {'mensagem': f'Sem escalas para excluir do mês de {mes}/{ano}', 'nivel': 'error'}
                    raise
                return {'mensagem': 'Escalas excluídas com sucesso', 'nivel': 'success'}
            finally:
                driver.quit()

        tarefa = iniciar_tarefa(tipo='pos_calculo.excluir_escalas', usuario=usuario,
                                template_resultado='pos_calculo/excluir_escalas.html', func=worker,
                                lock_key=_LOCK_SELENIUM)
        return redirect('tarefa_acompanhar', tarefa_id=tarefa.id)
    return render(request, "pos_calculo/excluir_escalas.html")
