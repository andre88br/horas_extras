from datetime import datetime

from empregados.models import Empregado, CargaHoraria, Importacoes


def salva_empregado(empregado, mes, ano, usuario):
    Importacoes.objects.update_or_create(mes=mes, ano=ano, tipo='empregados', defaults={
        'importado_por_id': usuario.id,
        'importado_por': usuario.username,
        'data_upload': datetime.now(),
    })
    importacao = Importacoes.objects.get(mes=mes, ano=ano, tipo='empregados')

    document = Empregado.objects.update_or_create(matricula=empregado[0], importacao=importacao, defaults={
        'matricula': empregado['matricula'],
        'nome': empregado['nome'],
        'salario': empregado['salario'],
        'insalubridade': empregado['insalubridade'],
        'data_atualizacao': datetime.now(),
        'mes': mes,
        'ano': ano,
    })
    return document


def salva_carga_horaria(fields, mes, ano, usuario):
    Importacoes.objects.update_or_create(mes=mes, ano=ano, tipo='carga_horaria', defaults={
        'importado_por_id': usuario.id,
        'importado_por': usuario.username,
        'data_upload': datetime.now(),
    })
    importacao = Importacoes.objects.get(mes=mes, ano=ano, tipo='carga_horaria')
    empregado = Empregado.objects.get(matricula=fields['matricula'], mes=mes, ano=ano)
    if empregado:
        document = CargaHoraria.objects.update_or_create(empregado=empregado, defaults={
            'importacao': importacao,
            'nome': fields['nome'],
            'carga_horaria': int(fields['carga_horaria']) / 6 * 30 if int(fields['carga_horaria']) <= 40 else int(fields['carga_horaria']),
            'importado_por': usuario.username,
            'importado_por_id': usuario.id,
        })
        return document

