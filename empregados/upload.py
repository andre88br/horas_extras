import pandas as pd
from django.core.exceptions import ObjectDoesNotExist

from arruma_arquivos import arruma_rubricas_calculadas, arruma_carga_horaria
from empregados.dbchanges import salva_empregado, salva_carga_horaria


def importa_empregados(usuario, mes, ano, planilha_salarios, planilha_insalubridades, planilha_carga_horaria,
                       progress_callback=None):
    empregados_a_mostrar = []
    salarios, insalubridades = '', ''
    try:
        if planilha_salarios != '' and planilha_salarios is not None:
            salarios = arruma_rubricas_calculadas(planilha_salarios)
            if str(salarios) == 'Erro':
                return 'Erro'
            salarios = salarios.rename(columns={'valor': 'salario'})
        if planilha_insalubridades != '' and planilha_insalubridades is not None:
            insalubridades = arruma_rubricas_calculadas(planilha_insalubridades)
            if str(insalubridades) == 'Erro':
                return 'Erro'
            insalubridades = insalubridades.rename(columns={'valor': 'insalubridade'})

        empregados = pd.merge(salarios, insalubridades, on=["matricula", "nome"], how="left")
        empregados = empregados.dropna(subset='nome')
        empregados.salario = empregados.salario.astype(float)
        empregados.insalubridade = empregados.insalubridade.astype(float)
        empregados = empregados.fillna(0.00)

        total = len(empregados) or 1
        for indice, (i, j) in enumerate(empregados.iterrows()):
            empregado = j
            document = salva_empregado(empregado, mes, ano, usuario)
            empregados_a_mostrar.append(document)
            if progress_callback:
                progress_callback(int((indice + 1) / total * 70), 'Importando empregados...')

        if planilha_carga_horaria != '' and planilha_carga_horaria is not None:
            carga_horaria = arruma_carga_horaria(planilha_carga_horaria, mes, ano)
            if str(carga_horaria) == 'Erro':
                return 'Erro'

            total_carga = len(carga_horaria) or 1
            for indice, (i, j) in enumerate(carga_horaria.iterrows()):
                salva_carga_horaria(j, mes, ano, usuario)
                if progress_callback:
                    progress_callback(70 + int((indice + 1) / total_carga * 30), 'Importando carga horária...')

        if len(empregados_a_mostrar) == 0:
            return "arquivo_vazio"
        else:
            resposta = "OK"
            return resposta
    except IndexError:
        resposta = "dados_inválidos"
        return resposta
    except ObjectDoesNotExist:
        resposta = "arquivo_vazio"
        return resposta


