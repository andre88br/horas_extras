import locale
from django import template
from datetime import date, datetime

register = template.Library()

locale.setlocale(locale.LC_MONETARY, "pt-BR.UTF-8")


@register.filter
def formata_valor(valor):
    return locale.currency(float(valor), symbol=True, grouping=True)


@register.filter
def formata_data(data):
    data = str(data).split(" ")[0]
    dia = int(data.split("-")[2])
    mes = int(data.split("-")[1])
    ano = int(data.split("-")[0])
    return date(ano, mes, dia).strftime("%d/%m/%Y")


@register.filter
def formata_data_hora(data):
    return datetime.strftime(data, "%d/%m/%Y - %H:%M:%S")


@register.filter
def converte_str(texto):
    texto = str(texto)
    return str.zfill(texto, 4)
