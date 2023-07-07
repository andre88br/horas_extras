from django import forms
from django.forms import SelectDateWidget


class TipoForm(forms.Form):
    tipo = forms.ChoiceField(choices=[('', ''),
                                      ('PlanilhaSolicitação', 'SOLICITAÇÃO'),
                                      ('PlanilhaConfirmação', 'CONFIRMAÇÃO')], initial='', required=True)


class DivForm(forms.Form):
    divisoes = ['', 'ADMINISTRATIVA', 'ASSISTENCIAL']

    divisao = forms.ChoiceField(choices=[(divisao, divisao) for divisao in divisoes], initial='', required=True)


class SetForm(forms.Form):
    ass = ['', 'UNIDADE DA CRIANCA E DO ADOLESCENTE', 'UNIDADE DE ANATOMIA PATOLOGICA',
           'UNIDADE DE APOIO A GESTAO EM ENFERMAGEM', 'UNIDADE DE ATENCAO DOMICILIAR E DOS CUIDADOS PALIATIVOS',
           'UNIDADE DE BLOCO CIRURGICO E PROCESSAMENTO MATERIAL ESTERILIZADO', 'UNIDADE DE CABECA E PESCOCO',
           'UNIDADE DE CLINICA CIRURGICA', 'UNIDADE DE CLINICA MEDICA', 'UNIDADE DE DIAGNOSTICO POR IMAGEM',
           'UNIDADE DE FARMACIA CLINICA E DISPENSACAO FARMACEUTICA', 'UNIDADE DE HEMATOLOGIA E HEMOTERAPIA',
           'UNIDADE DE LABORATORIO DE ANALISES CLINICAS', 'UNIDADE DE NUTRICAO CLINICA', 'UNIDADE DE ONCOLOGIA',
           'UNIDADE DE REABILITACAO', 'UNIDADE DE SAUDE DA MULHER', 'UNIDADE DE SAUDE MENTAL',
           'UNIDADE DE SISTEMA URINARIO', 'UNIDADE DE TERAPIA INTENSIVA ADULTO',
           'UNIDADE DE TERAPIA INTENSIVA NEONATAL',
           'UNIDADE DE TRAUMATO-ORTOPEDIA', 'UNIDADE DE URGENCIA E EMERGENCIA', 'UNIDADE DO SISTEMA CARDIOVASCULAR',
           'UNIDADE DO SISTEMA DIGESTIVO', 'UNIDADE DO SISTEMA NEUROLOGICO', 'UNIDADE DO SISTEMA RESPIRATORIO']

    adm = ['', 'UNIDADE DE PLANEJAMENTO E DIMENSIONAMENTO DE ESTOQUES',
           'UNIDADE DE ALMOXARIFADO E CONTROLE DE ESTOQUES']

    setor = forms.ChoiceField(choices=[(setor, setor) for setor in ass], initial='', required=False)

    setor2 = forms.ChoiceField(choices=[(setor, setor) for setor in adm], initial='', required=False)


class MonthYearWidget(SelectDateWidget):
    def __init__(self, *args, **kwargs):
        kwargs['empty_label'] = ('Year', 'Month', 'Day')
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        select_widgets = context['widget']['subwidgets']

        # Removendo o campo de dia
        del select_widgets[0]

        return context


class DateForm(forms.Form):
    data = forms.DateField(widget=MonthYearWidget, required=True)


class SetorForm(forms.Form):
    unidades = ['', 'UNIDADE DA CRIANCA E DO ADOLESCENTE', 'UNIDADE DE ANATOMIA PATOLOGICA',
                'UNIDADE DE APOIO A GESTAO EM ENFERMAGEM', 'UNIDADE DE ATENCAO DOMICILIAR E DOS CUIDADOS PALIATIVOS',
                'UNIDADE DE BLOCO CIRURGICO E PROCESSAMENTO MATERIAL ESTERILIZADO', 'UNIDADE DE CABECA E PESCOCO',
                'UNIDADE DE CLINICA CIRURGICA', 'UNIDADE DE CLINICA MEDICA', 'UNIDADE DE DIAGNOSTICO POR IMAGEM',
                'UNIDADE DE FARMACIA CLINICA E DISPENSACAO FARMACEUTICA', 'UNIDADE DE HEMATOLOGIA E HEMOTERAPIA',
                'UNIDADE DE LABORATORIO DE ANALISES CLINICAS', 'UNIDADE DE NUTRICAO CLINICA', 'UNIDADE DE ONCOLOGIA',
                'UNIDADE DE REABILITACAO', 'UNIDADE DE SAUDE DA MULHER', 'UNIDADE DE SAUDE MENTAL',
                'UNIDADE DE SISTEMA URINARIO', 'UNIDADE DE TERAPIA INTENSIVA ADULTO',
                'UNIDADE DE TERAPIA INTENSIVA NEONATAL', 'UNIDADE DE TRAUMATO-ORTOPEDIA',
                'UNIDADE DE URGENCIA E EMERGENCIA', 'UNIDADE DO SISTEMA CARDIOVASCULAR', 'UNIDADE DO SISTEMA DIGESTIVO',
                'UNIDADE DO SISTEMA NEUROLOGICO', 'UNIDADE DO SISTEMA RESPIRATORIO',
                'UNIDADE DE PLANEJAMENTO E DIMENSIONAMENTO DE ESTOQUES',
                'UNIDADE DE ALMOXARIFADO E CONTROLE DE ESTOQUES']

    setor = forms.ChoiceField(choices=[(setor, setor) for setor in unidades], initial='', required=False)
