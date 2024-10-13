from django.shortcuts import render
from .forms import AutomatoForm
from itertools import combinations
from automathon import DFA

# Função para encontrar o estado final de uma transição, dado um estado inicial e um caractere de transição
def estado_final_transicao(transicoes, estadoInicial, caracter):
    for transicao in transicoes:
        estadoInicialTransicao, estadoFinalTransicao, caracterTransicao = transicao.split(',')

        if estadoInicialTransicao == estadoInicial and caracterTransicao == caracter:
            return estadoFinalTransicao

# Função para validar se uma tupla de estados deve ser marcada como combinada
def validar_tupla(tuplasEstados, combinacoesDict, transicoes, alfabeto, steps):
    alteracao = False  # Acompanhar se houve alguma alteração nas combinações

    for tupla in tuplasEstados:
        if not combinacoesDict.get(''.join(tupla)):
            for caracter in alfabeto:
                # Obtém os estados finais das transições para os dois estados na tupla
                tuplaTransicao = (
                    estado_final_transicao(transicoes, tupla[0], caracter),
                    estado_final_transicao(transicoes, tupla[1], caracter)
                )
                if combinacoesDict.get(''.join(tuplaTransicao), False) or combinacoesDict.get(''.join(reversed(tuplaTransicao)), False):
                    combinacoesDict[''.join(tupla)] = True
                    alteracao = True
                    steps.append(f"Combinando estados {tupla[0]} e {tupla[1]} porque suas transições para '{caracter}' levam a estados já combinados.")
    return alteracao

def validar_entrada(alfabeto:list, estados:list, inicial:str, finais:list, transicoes:list):
    if (alfabeto == ['']) or (not estados) or (inicial == ''):
        return False, f"Parâmetro de inicialização vazio."

    # Verifica se o estado inicial pertence ao conjunto de estados
    if inicial not in estados:
        return False, f"O estado inicial {inicial} não pertence ao conjunto de estados."
    
    # Verifica se o subconjunto de estados finais pertencem ao conjunto de estados
    for estado in finais:
        if estado not in estados and estado != '':
            return False, f"O estado final {estado} não pertence ao conjunto de estados."
        
    # Lista das ligações obrigatórias
    comb_obrigatorias = [(est, simb) for est in estados for simb in alfabeto]

    for transicao in transicoes:
        # Valida as transições
        if len(transicao.split(",")) != 3:
            return False, f"Transição \"{transicao}\" inválida."
        
        estadoInicial, estadoFinal, simbTransicao = transicao.split(",")
        if (estadoInicial not in estados) or (estadoFinal not in estados) or (simbTransicao not in alfabeto):
            return False, f"Transição \"{transicao}\" inválida."
        
        # Verifica se todas as ligações obrigatórias foram feitas
        if (estadoInicial, simbTransicao) in comb_obrigatorias:
            comb_obrigatorias.remove((estadoInicial, simbTransicao))
        else:
            return False, f"Verifique a transição \"{transicao}\""
        
    # Quando faltam ligações obrigatórias a serem feitas
    if len(comb_obrigatorias) > 0:
        transFaltosas = set(transicao[0] for transicao in comb_obrigatorias)
        string = ', '.join(transFaltosas)
        return False, f"Os seguintes estados estão com transições faltosas: {string}"

    return True, f"O AFD é válido."

def remove_estado_inutil(estados: list, transicoes: list, inicial: str, steps: list):
    # Busca em profundidade para marcar estados alcançáveis a partir do estado inicial
    def dfs(estado_atual, estados_alcancaveis, transicoes):
        estados_alcancaveis.add(estado_atual)
        for transicao in transicoes:
            estadoInicial, estadoFinal, simbTransicao = transicao.split(",")
            # Percorre na forma de pilha
            if (estadoInicial == estado_atual) and (estadoFinal not in estados_alcancaveis):
                dfs(estadoFinal, estados_alcancaveis, transicoes)

    estados_alcancaveis = set()
    
    steps.append(f"Iniciando busca de estados alcançáveis a partir do estado inicial '{inicial}'.")
    dfs(inicial, estados_alcancaveis, transicoes)
    steps.append(f"Estados alcançáveis: {', '.join(estados_alcancaveis)}.")

    estados_inatingiveis = [estado for estado in estados if estado not in estados_alcancaveis]
    if estados_inatingiveis:
        steps.append(f"Removendo estados inatingíveis: {', '.join(estados_inatingiveis)}.")
    # Remove estaod inuteis do input
    for inutil in estados_inatingiveis:
        estados.remove(inutil)
        for transicao in transicoes:
            if inutil in transicoes:
                transicoes.remove(transicao)

def automato_view(request):
    steps = []  # Lista para armazenar os passos do processo (para debug)
    if request.method == 'POST':
        form = AutomatoForm(request.POST, request.FILES)
        if form.is_valid():
            arquivo_txt = request.FILES.get('arquivo_txt')

            if arquivo_txt:
                # Processar o arquivo de texto
                dados_arquivo = arquivo_txt.read().decode('utf-8')
                linhas = dados_arquivo.strip().splitlines()

                alfabeto, estados, inicial, finais, transicoes = None, None, None, None, []

                for linha in linhas:
                    if linha.startswith('alfabeto:'):
                        alfabeto = linha.split(':')[1].strip().split(',')
                    elif linha.startswith('estados:'):
                        estados = linha.split(':')[1].strip().split(',')
                    elif linha.startswith('inicial:'):
                        inicial = linha.split(':')[1].strip()
                    elif linha.startswith('finais:'):
                        finais = linha.split(':')[1].strip().split(',')
                    elif linha.startswith('transições'):
                        continue
                    else:
                        transicoes.append(linha.strip())
            else:
                # Extração do .txt
                alfabeto = form.cleaned_data['alfabeto'].strip().split(',')  
                estados = form.cleaned_data['estados'].strip().split(',')
                inicial = form.cleaned_data['inicial'].strip()
                finais = form.cleaned_data['finais'].strip().split(',')
                transicoes = [t.strip() for t in form.cleaned_data['transicoes'].split('\n')] # Transições, separadas e limpas

            # Validação da entrada
            validade, mensagem = validar_entrada(alfabeto, estados, inicial, finais, transicoes)
            steps.append(f"Validação da entrada: {mensagem}")

            if not validade:
                return render(request, 'tfm/home.html', {'form': form, 'mensagem': mensagem, 'steps': steps})

            # Remover estados inatingíveis
            remove_estado_inutil(estados, transicoes, inicial, steps)

            # Cria todas as combinações possíveis de pares de estados
            tuplasEstados = [tuple(tupla) for tupla in combinations(estados, 2)]
            steps.append(f"Gerando combinações de estados: {', '.join(['('+','.join(tupla)+')' for tupla in tuplasEstados])}.")

            # Une os elementos de cada par para criar um identificador único
            combinacoesDict = {''.join(par): False for par in tuplasEstados}
            steps.append("Inicializando dicionário de combinações com valores False.")

            # Marca pares de estados onde apenas um dos pares é final
            for tupla in tuplasEstados:
                if (tupla[0] in finais and tupla[1] not in finais) or (tupla[0] not in finais and tupla[1] in finais):
                    combinacoesDict[''.join(tupla)] = True  # Marca como True para distinguir estados finais e não finais
                    steps.append(f"Marcando combinação {tupla[0]} e {tupla[1]} como distinta (um final e outro não).")

            # Checa alterações durante a validação de tuplas
            alteracao = True
            while alteracao:
                # Valida as tuplas de estados e atualiza combinacoesDict
                alteracao = validar_tupla(tuplasEstados, combinacoesDict, transicoes, alfabeto, steps)
                if alteracao:
                    steps.append("Encontrou combinações para marcar como equivalentes.")

            # Adiciona estados equivalentes que podem ser unidos à lista uniaoEstados
            uniaoEstados = [tupla for tupla in tuplasEstados if not combinacoesDict.get(''.join(tupla))]
            steps.append(f"Estados equivalentes não marcados: {', '.join(['('+','.join(tupla)+')' for tupla in uniaoEstados])}.")

            repetidos = []
            # Encontra pares de tuplas com estados comuns para unificação
            for i, tupla1 in enumerate(uniaoEstados):
                for j in range(i + 1, len(uniaoEstados)):
                    tupla2 = uniaoEstados[j]
                    if any(elem in tupla2 for elem in tupla1):  # Verifica estados comuns
                        repetidos.append((tupla1, tupla2))
                        steps.append(f"Encontrado estados comuns entre {tupla1} e {tupla2}.")

            # Juntar todos os pares de estados repetidos em um único conjunto
            grupos = []  # Armazenar os grupos de equivalência
            for tupla in repetidos:
                encontrado = False
                for grupo in grupos:
                    # Verifica se algum elemento da tupla já está no grupo
                    if any(elem in grupo for elem in tupla):
                        grupo.update(tupla)  # Atualiza o grupo com os novos elementos
                        encontrado = True
                        steps.append(f"Atualizando grupo de equivalência com {tupla}.")
                        break
                if not encontrado:
                    grupos.append(set(tupla))  # Cria um novo grupo com a tupla atual
                    steps.append(f"Criação de novo grupo de equivalência com {tupla}.")

            repetidos = []
            for grupo in grupos:  # Itera sobre cada grupo na lista de grupos
                uniao = set()  # Cria um conjunto vazio para armazenar a união dos elementos (elimina duplicatas)
                
                for tupla in grupo:  # Itera sobre cada tupla dentro do grupo
                    uniao.update(tupla)  # Atualiza o conjunto `uniao` com os elementos da tupla (adiciona sem duplicatas)
                uniao = list(uniao)  # Converte o conjunto `uniao` de volta para uma lista
                if uniao[0].isdigit():  # Verifica se o primeiro elemento da lista é um número (todos devem ser números se o primeiro for)
                    uniao = sorted(map(int, uniao))  # Converte os elementos para inteiros e os ordena numericamente
                    uniao = list(map(str, uniao))  # Converte os elementos de volta para strings
                else:
                    uniao = sorted(uniao)  # Se não for número, apenas ordena alfabeticamente
                
                repetidos.append(uniao)  # Adiciona a lista `uniao` (ordenada e processada) à lista `repetidos`
                steps.append(f"Grupo de equivalência unido: {', '.join(uniao)}.")

            # Remove pares de uniaoEstados que tenham elementos já unidos na lista "uniao"
            remover = []
            for grupo in repetidos:
                for element in grupo:
                    for estado in uniaoEstados:
                        if element in estado:
                            if estado not in remover: 
                                remover.append(estado)
            if remover:
                steps.append(f"Removendo estados combinados: {', '.join(remover)}.")
            for tupla in remover:
                uniaoEstados.remove(tupla)
            
            # Adiciona o conjunto unido de estados em uniaoEstados
            if repetidos:
                for grupo in repetidos:
                    uniaoEstados.append(grupo)
                    steps.append(f"Adicionando grupo unido: {', '.join(grupo)}.")

            # Adiciona estados não equivalentes diretamente na lista
            for estado in estados:
                if not any(estado in tupla for tupla in uniaoEstados):
                    uniaoEstados.append(estado)
                    steps.append(f"Adicionando estado não equivalente: {estado}.")

            # Constrói a lista de estados minimizados para a AFD
            afdMinimizada = []
            
            for element in uniaoEstados:
                if inicial in element:  # Verifica se o valor de `inicial` está presente na lista `uniao`
                    inicial = ''.join(element)  # Se estiver, junta todos os elementos da lista `uniao` em uma única string
                    steps.append(f"Atualizando estado inicial para: {inicial}.")
                afdMinimizada.append(''.join(element))  # Concatena os estados unidos para a forma minimizada
                steps.append(f"Adicionando estado minimizado: {''.join(element)}.")

            # Atualiza o contexto com a AFD minimizada
            context = {
                'alfabeto': alfabeto,
                'estados': estados,
                'inicial': inicial,
                'finais': finais,
                'transicoes': transicoes,
                'combinacoesDict': combinacoesDict,
                'afdMinimizada': afdMinimizada,
                'steps': steps  # Adicionando os passos ao contexto
            }

            novasTransicoes = []  # Lista para armazenar as novas transições

            # Itera sobre cada transição na lista `transicoes`
            for transicao in transicoes:
                # Divide a transição em três partes: estado inicial, estado final e o caractere da transição
                estadoInicialTransicao, estadoFinalTransicao, caracterTransicao = transicao.split(',')
                # Itera sobre cada estado no conjunto `afdMinimizada` para encontrar o estado inicial minimizado
                for estadoInicialMin in afdMinimizada:
                    # Verifica se o estado inicial da transição faz parte do estado minimizado atual
                    if estadoInicialTransicao in estadoInicialMin:
                        # Itera sobre cada estado no conjunto `afdMinimizada` para encontrar o estado final minimizado
                        for estadoMinimizado in afdMinimizada:
                            # Verifica se o estado final da transição faz parte do estado minimizado atual
                            if estadoFinalTransicao in estadoMinimizado:
                                # Cria uma nova transição no formato "estadoInicial,estadoMinimizado,caracterTransicao"
                                novaTransicao = f"{estadoInicialMin},{estadoMinimizado},{caracterTransicao}"
                                # Adiciona a nova transição à lista `novasTransicoes` se ainda não estiver presente
                                if novaTransicao not in novasTransicoes:
                                    novasTransicoes.append(novaTransicao)
                                    steps.append(f"Adicionando transição minimizada: {novaTransicao}.")

            # Lista para armazenar os novos estados finais minimizados
            novoEstadosFinais = []
            # Itera sobre cada estado no conjunto `afdMinimizada`
            for estado in afdMinimizada:
                # Verifica se qualquer estado final original está contido no estado minimizado
                if any(elem in estado for elem in finais):
                    novoEstadosFinais.append(estado)  # Adiciona o estado minimizado à lista de estados finais
                    steps.append(f"Adicionando estado final minimizado: {estado}.")

            transicoesDict = {}
            for transicao in novasTransicoes:
                estadoInicialTransicao, estadoFinalTransicao, caracterTransicao = transicao.split(',')
                    
                # Verifica se o estado inicial já existe no dicionário
                if estadoInicialTransicao not in transicoesDict:
                    transicoesDict[estadoInicialTransicao] = {}  # Cria um dicionário vazio para o estado inicial    
                # Adiciona a transição ao dicionário
                transicoesDict[estadoInicialTransicao][caracterTransicao] = estadoFinalTransicao   
                steps.append(f"Atualizando dicionário de transições: {transicao}.")

            automata = DFA(afdMinimizada, alfabeto, transicoesDict, inicial, novoEstadosFinais)
            automata.view("tfm\static\imagem\AFD_MIN")

            # Atualiza o contexto com a AFD minimizada e os passos
            context = {
                'alfabeto': alfabeto,
                'estados': estados,
                'inicial': inicial,
                'finais': finais,
                'transicoes': transicoes,
                'combinacoesDict': combinacoesDict,
                'afdMinimizada': afdMinimizada,
                'steps': steps,
                'novasTransicoes': novasTransicoes,
                'novoEstadosFinais': novoEstadosFinais,
                'transicoesDict': transicoesDict 
            }


            return render(request, 'tfm\\automato_result.html', context)
    else:
        form = AutomatoForm()
    
    return render(request, 'tfm\\home.html', {'form': form})
