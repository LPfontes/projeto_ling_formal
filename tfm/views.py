from django.shortcuts import render
from .forms import AutomatoForm
from itertools import combinations
def automato_view(request):
    if request.method == 'POST':
        form = AutomatoForm(request.POST)
        if form.is_valid():
            # Lógica para processar os dados
            alfabeto = form.cleaned_data['alfabeto'].split(',')
            estados = form.cleaned_data['estados'].split(',')
            inicial = form.cleaned_data['inicial']
            finais = form.cleaned_data['finais'].split(',')
            transicoes = [t.strip() for t in form.cleaned_data['transicoes'].split('\n')]
            
            
            
            tuplasEstados = [tuple(reversed(tupla)) for tupla in combinations(estados, 2)] # criamos as combinações dos estados como em q1,q2,q3 = (q1,q2), (q1,q3) e (q2,q3)
            uniaoEstados = [''.join(par) for par in tuplasEstados]
            combinacoesDict = {combinacao: False for combinacao in uniaoEstados}

            for tupla in tuplasEstados: # marcamos os estados onde apenas um dos pares é Estado final
                if(tupla[0] in finais and not tupla[1] in finais or not tupla[0] in finais and tupla[1] in finais):
                    combinacoesDict[''.join(tupla)] = True
            
            
            context = {
                'alfabeto': alfabeto,
                'estados': estados,
                'inicial': inicial,
                'finais': finais,
                'transicoes': transicoes,
                'combinacoesDict': combinacoesDict,  # Passando as combinações para o template
            }

            return render(request, 'tfm\\automato_result.html', context)
    else:
        form = AutomatoForm()
    
    return render(request, 'tfm\home.html', {'form': form})
