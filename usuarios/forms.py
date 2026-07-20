from datetime import datetime

import pandas as pd
from django import forms
from django.contrib.auth.models import User

from empregados.models import Importacoes

current_year = datetime.now().year
tudo = Importacoes.objects.values()
tudo = pd.DataFrame(tudo)
years = [2022]
years_array = tudo.ano.unique() if 'ano' in tudo.columns else []

for year in years_array:
    years.append(year)
    years = sorted(years)


class UsuariosForm(forms.Form):
    username = forms.CharField(label="Usuário", max_length=100, initial=User.username)
    user = forms.EmailField(label="Usuário", initial=User.username)


class YearForm(forms.Form):
    year = forms.ChoiceField(choices=[(year, year) for year in years], initial=current_year)
