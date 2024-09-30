from django.shortcuts import render
from .forms import AutomatoForm
from itertools import combinations

def estado_final_transicao(transicoes,estadoInicial,caracter):
    for transicao in transicoes:
        estadoInicialTransicao, estadoFinalTransicao, caracterTransicao = transicao.split(',')
        if estadoInicialTransicao == estadoInicial and caracterTransicao == caracter:
            return estadoFinalTransicao
def validar_tupla(tupla,combinacoesDict,transicoes,valorTrasicao):

    tuplaTrasicao = estado_final_transicao(transicoes,tupla[0],valorTrasicao),estado_final_transicao(transicoes,tupla[1],valorTrasicao)
    if combinacoesDict.get(''.join(tuplaTrasicao),0):
        combinacoesDict[''.join(tupla)] = True
    
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
            uniaoEstados = []
            for tupla in tuplasEstados: # marcamos os estados onde apenas um dos pares é Estado final
                if(tupla[0] in finais and not tupla[1] in finais or not tupla[0] in finais and tupla[1] in finais):
                    combinacoesDict[''.join(tupla)] = True
            
            for tupla in tuplasEstados: # marcamos os estados onde as transições de cada par levam a um novo par existente e já marcado
                if not combinacoesDict.get(''.join(tupla)):
                    for caracter in alfabeto:
                        validar_tupla(tupla,combinacoesDict,transicoes,caracter)
            afdMinimizada = []
            for tupla in tuplasEstados: # adicionamos a lista os estados que não são equivalentes
                if combinacoesDict.get(''.join(tupla)):
                    afdMinimizada.append(tupla[0])
                    afdMinimizada.append(tupla[1])
                else:
                     uniaoEstados.append(tupla) # adicionamos a lista os estados são equivalentes e podem ser unidos
            
            for i, tupla1 in enumerate(uniaoEstados):
                repetidos = []
                for j in range(i, len(uniaoEstados)):  # j começa no índice i
                    tupla2 = uniaoEstados[j]
                    # Não comparar a tupla com ela mesma
                    if i != j:
                        # Verifica se algum elemento de tupla1 está em tupla2
                        if any(elem in tupla2 for elem in tupla1):
                            repetidos.append((tupla1, tupla2))
            
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
 