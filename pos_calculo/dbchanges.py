from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist

from empregados.models import Importacoes, Empregado
from pos_calculo.models import RelatorioBatidasRejeitadas, RelatorioBancosRecalculados, RelatorioRubricasLancadas


def salva_rejeitada(fields, usuario, mes, ano, data):
    Importacoes.objects.update_or_create(mes=mes, ano=ano, tipo='rejeitadas', defaults={
            'importado_por_id': usuario.id,
            'importado_por': usuario.username,
            'data_upload': datetime.now(),
        })
    importacao = Importacoes.objects.get(mes=mes, ano=ano, tipo='rejeitadas')
    try:
        empregado = Empregado.objects.get(matricula=fields['matricula'], mes=mes, ano=ano)
        batida1 = RelatorioBatidasRejeitadas.objects.filter(empregado__matricula=fields['matricula'],
                                                            data=data, batida=1)
        batida2 = RelatorioBatidasRejeitadas.objects.filter(empregado__matricula=fields['matricula'],
                                                            data=data, batida=2)
        if not batida1:
            if empregado:
                document = RelatorioBatidasRejeitadas.objects.update_or_create(
                    empregado=empregado, importacao=importacao,
                    data=data, batida=1, defaults={
                        'nome': str(fields['nome']).upper(),
                        'data_upload': datetime.now(),
                        'importado_por': usuario.username,
                        'importado_por_id': usuario.id,
                        'tipo': fields['tipo'],
                    })
                return document
        elif not batida2:
            if empregado:
                document = RelatorioBatidasRejeitadas.objects.update_or_create(
                    empregado=empregado, importacao=importacao,
                    data=data, batida=2, defaults={
                        'nome': str(fields['nome']).upper(),
                        'data_upload': datetime.now(),
                        'importado_por': usuario.username,
                        'importado_por_id': usuario.id,
                        'tipo': fields['tipo'],
                    })
                return document

    except ObjectDoesNotExist as erro:
        print(f'Erro: {erro}')
        pass


def salva_banco_recalculado(fields, usuario, mes, ano):
    Importacoes.objects.update_or_create(mes=mes, ano=ano, tipo='banco_recalculado', defaults={
            'importado_por_id': usuario.id,
            'importado_por': usuario.username,
            'data_upload': datetime.now(),
        })
    importacao = Importacoes.objects.get(mes=mes, ano=ano, tipo='banco_recalculado')
    try:
        empregado = Empregado.objects.get(matricula=fields['matricula'], mes=mes, ano=ano)
        if empregado:
            document = RelatorioBancosRecalculados.objects.update_or_create(
                empregado=empregado, importacao=importacao, defaults={
                    'nome': str(fields['nome']).upper(),
                    'data_upload': datetime.now(),
                    'importado_por': usuario.username,
                    'importado_por_id': usuario.id,
                })
            return document
    except ObjectDoesNotExist as erro:
        print(f'Erro: {erro}')
        pass


def salva_rubricas_lancadas(fields, usuario, mes, ano, rubrica, valor):
    Importacoes.objects.update_or_create(mes=mes, ano=ano, tipo='rubricas_lancadas', defaults={
            'importado_por_id': usuario.id,
            'importado_por': usuario.username,
            'data_upload': datetime.now(),
        })
    importacao = Importacoes.objects.get(mes=mes, ano=ano, tipo='rubricas_lancadas')
    try:
        empregado = Empregado.objects.get(matricula=fields['matricula'], mes=mes, ano=ano)
        if empregado:
            document = RelatorioRubricasLancadas.objects.update_or_create(
                empregado=empregado, importacao=importacao, rubrica=rubrica, defaults={
                    'nome': str(fields['nome']).upper(),
                    'valor': valor,
                    'data_upload': datetime.now(),
                    'importado_por': usuario.username,
                    'importado_por_id': usuario.id,
                })
            return document
    except ObjectDoesNotExist as erro:
        print(f'Erro: {erro}')
        pass
