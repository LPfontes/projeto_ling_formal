from django.shortcuts import render
from .forms import AutomatoForm
from itertools import combinations

def estado_final_transicao(transicoes,estadoInicial,caracter):
    for transicao in transicoes:
        estadoInicialTransicao, estadoFinalTransicao, caracterTransicao = transicao.split(',')
        if estadoInicialTransicao == estadoInicial and caracterTransicao == caracter:
            return estadoFinalTransicao
def validar_tupla(tuplasEstados,combinacoesDict,transicoes,alfabeto):
    alteracao = False
    for tupla in tuplasEstados: # marcamos os estados onde as transições de cada par levam a um novo par existente e já marcado
        if not combinacoesDict.get(''.join(tupla)):
            for caracter in alfabeto:
                tuplaTrasicao = estado_final_transicao(transicoes,tupla[0],caracter),estado_final_transicao(transicoes,tupla[1],caracter)
                if combinacoesDict.get(''.join(tuplaTrasicao), 0) or combinacoesDict.get(''.join(reversed(tuplaTrasicao)), 0):
                    combinacoesDict[''.join(tupla)] = True
                    alteracao = True
    return alteracao
    
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
            alteracao = True
            while(alteracao):
                alteracao = validar_tupla(tuplasEstados,combinacoesDict,transicoes,alfabeto)
            
            for tupla in tuplasEstados: 
                if not combinacoesDict.get(''.join(tupla)):
                    uniaoEstados.append(tupla) # adicionamos a lista os estados são equivalentes e podem ser unidos
            repetidos = []
            for i, tupla1 in enumerate(uniaoEstados):
                for j in range(i, len(uniaoEstados)):  # j começa no índice i
                    tupla2 = uniaoEstados[j]
                    # Não comparar a tupla com ela mesma
                    if i != j:
                        # Verifica se algum elemento de tupla1 está em tupla2
                        if any(elem in tupla2 for elem in tupla1):
                            repetidos.append((tupla1, tupla2))

            uniao = set()
            # Juntar todas as tuplas de repetidos em um único conjunto
            for par in repetidos:
                # Adiciona os elementos de ambas as tuplas no conjunto
                for tupla in par:
                    uniao.update(tupla)   
            remover = []
            for tupla in uniaoEstados:
                if any(elem in tupla for elem in uniao):
                    remover.append(tupla)
            for tupla in remover:
                uniaoEstados.remove(tupla)
            uniaoEstados.append(uniao)
            for estado in estados:
                if not any(estado in tupla for tupla in uniaoEstados):
                    uniaoEstados.append(estado)
            afdMinimizada = []
            for element in uniaoEstados: 
                afdMinimizada.append(''.join(element))

                    
            context = {
                'alfabeto': alfabeto,
                'estados': estados,
                'inicial': inicial,
                'finais': finais,
                'transicoes': transicoes,
                'combinacoesDict': combinacoesDict,  # Passando as combinações para o template
                'afdMinimizada':afdMinimizada
            }

            return render(request, 'tfm\\automato_result.html', context)
    else:
        form = AutomatoForm()
    
    return render(request, 'tfm\home.html', {'form': form})
 