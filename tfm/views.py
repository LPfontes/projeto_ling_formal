from django.shortcuts import render
from .forms import AutomatoForm
from itertools import combinations
from automathon import DFA
# Função para encontrar o estado final de uma transição, dado um estado inicial e um caractere de transição
def estado_final_transicao(transicoes, estadoInicial, caracter):
    for transicao in transicoes:
        # Desempacota a string de transição no formato "estadoInicial,estadoFinal,caracter"
        estadoInicialTransicao, estadoFinalTransicao, caracterTransicao = transicao.split(',')        
        # Verifica se o estado inicial e o caractere da transição correspondem aos parâmetros passados
        if estadoInicialTransicao == estadoInicial and caracterTransicao == caracter:
            # Retorna o estado final da transição correspondente
            return estadoFinalTransicao
# Função para validar se uma tupla de estados deve ser marcada como combinada
def validar_tupla(tuplasEstados, combinacoesDict, transicoes, alfabeto):
    alteracao = False  # Variável para acompanhar se houve alguma alteração nas combinações
    # Itera sobre cada tupla de estados em `tuplasEstados`
    for tupla in tuplasEstados:
        # Verifica se a tupla ainda não foi marcada como combinada
        if not combinacoesDict.get(''.join(tupla)):
            # Verifica as transições para cada caractere do alfabeto
            for caracter in alfabeto:
                # Obtém os estados finais das transições para os dois estados na tupla
                tuplaTrasicao = (
                    estado_final_transicao(transicoes, tupla[0], caracter),
                    estado_final_transicao(transicoes, tupla[1], caracter)
                )
                # Verifica se a transição resulta em uma tupla que já está marcada como combinada,
                # seja na ordem direta ou reversa
                if combinacoesDict.get(''.join(tuplaTrasicao), 0) or combinacoesDict.get(''.join(reversed(tuplaTrasicao)), 0):
                    # Marca a tupla atual como combinada
                    combinacoesDict[''.join(tupla)] = True
                    alteracao = True  # Indica que houve uma alteração
    # Retorna se houve alguma alteração (True ou False)
    return alteracao
    
def automato_view(request):
    if request.method == 'POST':
        form = AutomatoForm(request.POST)
        if form.is_valid():
            # Extrai os dados do formulário e os processa
            alfabeto = form.cleaned_data['alfabeto'].split(',')  # Obtém o alfabeto e o separa em uma lista
            estados = form.cleaned_data['estados'].split(',')  # Obtém os estados e os separa em uma lista
            inicial = form.cleaned_data['inicial']  # Estado inicial
            finais = form.cleaned_data['finais'].split(',')  # Estados finais, separados em uma lista
            transicoes = [t.strip() for t in form.cleaned_data['transicoes'].split('\n')] # Transições, separadas e limpas

            # Cria todas as combinações possíveis de pares de estados e inverte cada tupla
            tuplasEstados = [tuple(reversed(tupla)) for tupla in combinations(estados, 2)]
            # Une os elementos de cada par para criar um identificador único
            uniaoEstados = [''.join(par) for par in tuplasEstados]
            combinacoesDict = {combinacao: False for combinacao in uniaoEstados}  # Inicializa o dicionário de combinações com valor False

            # Marca pares de estados onde apenas um dos pares é final
            for tupla in tuplasEstados:
                if (tupla[0] in finais and tupla[1] not in finais) or (tupla[0] not in finais and tupla[1] in finais):
                    combinacoesDict[''.join(tupla)] = True  # Marca como True para distinguir estados finais e não finais

            # Variável de controle para checar alterações durante a validação de tuplas
            alteracao = True
            while alteracao:
                # Valida as tuplas de estados e atualiza combinacoesDict
                alteracao = validar_tupla(tuplasEstados, combinacoesDict, transicoes, alfabeto)

            # Adiciona estados equivalentes que podem ser unidos à lista uniaoEstados
            uniaoEstados = [tupla for tupla in tuplasEstados if not combinacoesDict.get(''.join(tupla))]

            repetidos = []
            # Encontra pares de tuplas com estados comuns para unificação
            for i, tupla1 in enumerate(uniaoEstados):
                for j in range(i, len(uniaoEstados)):
                    tupla2 = uniaoEstados[j]
                    if i != j:
                        if any(elem in tupla2 for elem in tupla1):  # Verifica estados comuns
                            repetidos.append((tupla1, tupla2))

            # Juntar todos os pares de estados repetidos em um único conjunto
            uniao = set()
            for par in repetidos:
                for tupla in par:
                    uniao.update(tupla)

            # Remove pares de uniaoEstados que tenham elementos já unidos na lista "uniao"
            remover = [tupla for tupla in uniaoEstados if any(elem in tupla for elem in uniao)]
            for tupla in remover:
                uniaoEstados.remove(tupla)

            # Adiciona o conjunto unido de estados em uniaoEstados
            if uniao:
                uniaoEstados.append(uniao)

            # Adiciona estados não equivalentes diretamente na lista
            for estado in estados:
                if not any(estado in tupla for tupla in uniaoEstados):
                    uniaoEstados.append(estado)

            # Constrói a lista de estados minimizados para a AFD
            afdMinimizada = []
            for element in uniaoEstados:
                afdMinimizada.append(''.join(element))  # Concatena os estados unidos para a forma minimizada

            # Atualiza o contexto com a AFD minimizada
            context = {
                'alfabeto': alfabeto,
                'estados': estados,
                'inicial': inicial,
                'finais': finais,
                'transicoes': transicoes,
                'combinacoesDict': combinacoesDict,
                'afdMinimizada': afdMinimizada
            }
            novasTrasicaos = []  # Lista para armazenar as novas transições

            # Itera sobre cada transição na lista `transicoes`
            for transicao in transicoes:
            # Divide a transição em três partes: estado inicial, estado final e o caractere da transição
                estadoInicialTransicao, estadoFinalTransicao, caracterTransicao = transicao.split(',')
            # Itera sobre cada estado no conjunto `afdMinimizada` para encontrar o estado inicial minimizado
                for estadoInicial in afdMinimizada:
                # Verifica se o estado inicial da transição faz parte do estado minimizado atual
                    if estadoInicialTransicao in estadoInicial:
                    # Itera sobre cada estado no conjunto `afdMinimizada` para encontrar o estado final minimizado
                        for estadoFinal in afdMinimizada:
                        # Verifica se o estado final da transição faz parte do estado minimizado atual
                            if estadoFinalTransicao in estadoFinal:
                            # Cria uma nova transição no formato "estadoInicial,estadoFinal,caracterTransicao"
                                novaTrasicao = estadoInicial + "," + estadoFinal + "," + caracterTransicao
                            # Adiciona a nova transição à lista `novasTrasicaos` se ainda não estiver presente
                                if novaTrasicao not in novasTrasicaos:
                                    novasTrasicaos.append(novaTrasicao)
            # Lista para armazenar os novos estados finais minimizados
            novoEstadosFinais = []
            # Itera sobre cada estado no conjunto `afdMinimizada`
            for estado in afdMinimizada:
                # Verifica se qualquer estado final original está contido no estado minimizado
                if any(elem in estado for elem in finais):
                    novoEstadosFinais.append(estado)  # Adiciona o estado minimizado à lista de estados finais
                # Atualiza o estado inicial se o estado inicial original estiver contido no estado minimizado
                if inicial in estado:
                    inicial = estado  # Define o estado inicial minimizado como o novo estado inicial
            transicoesDict = {}
            for transicao in novasTrasicaos:
                estadoInicialTransicao, estadoFinalTransicao, caracterTransicao = transicao.split(',')
                    
                # Verifica se o estado inicial já existe no dicionário
                if estadoInicialTransicao not in transicoesDict:
                    transicoesDict[estadoInicialTransicao] = {}  # Cria um dicionário vazio para o estado inicial    
                # Adiciona a transição ao dicionário
                transicoesDict[estadoInicialTransicao][caracterTransicao] = estadoFinalTransicao   
            # criando a imagem da AFD
            automata = DFA(afdMinimizada, alfabeto, transicoesDict, inicial, novoEstadosFinais)
            automata.view("tfm\\static\\imagem\\AFD_MIN")
            # Renderiza a página de resultado com o contexto atualizado]
            return render(request, 'tfm\\automato_result.html', context)
    else:
        
        form = AutomatoForm()
    
    return render(request, 'tfm\home.html', {'form': form})
 