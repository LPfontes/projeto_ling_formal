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


def validar_entrada(alfabeto:list, estados:list, inicial:str, finais:list, transicoes:list):
    # Verifica se os parâmetros estão vazios
    if (alfabeto == ['']) or (estados == ['']) or (inicial == ''):
        return False, f"Parâmetro de inicialização vazio."

    # Verifica se o estado inicial pertence ao conjuto de estados
    if inicial not in estados:
        return False, f"O estado inicial {inicial} não pertence ao conjunto de estados."
    
    # Verifica se o subconjunto de estados finais pertencem ao conjunto de estados
    for estado in finais:
        if estado not in estados:
            return False, f"O estado final {estado} não pertence ao conjunto de estados."
        
    # Cria uma lista com todas as ligações obrigatórias que partem de cada estado
    comb_obrigatorias = [(est,simb) for est in estados for simb in alfabeto]

    # Verifica se as transições foram feitas de maneira correta
   
    for transicao in transicoes:
        if len(transicao) > 3:
            estadoInicial, estadoFinal, simbTransicao = transicao.split(",")
            # Verifica se cada compontente da transição pertence ao conjuto fornecido de entrada
            if (estadoInicial not in estados) or (estadoFinal not in estados) or (simbTransicao not in alfabeto):
                return False, f"Transição {transicao} inválida."
            # Faz a checagem das ligações obrigatórias, evitando redundâncias
            if (estadoInicial, simbTransicao) in comb_obrigatorias:
                comb_obrigatorias.remove((estadoInicial, simbTransicao))
            # Havendo mais de uma ligação com o mesmo simbolo, partindo do mesmo estado, retorna um erro
            else:
                return False, f"Verifique a transição {transicao}"
        else:
            return False, f"Transição {transicao} inválida."
    # Caso alguma ligação, que é obrigatória, não é realizada
    if len(comb_obrigatorias) > 0:
        transFaltosa = set(transicao[0] for transicao in comb_obrigatorias)
        string = ', '.join(transFaltosa)
        return False, f"Os seguintes estados estão com transições faltosas: {string}"

    return True, f"O AFD é válido."


def remove_estado_inutil(estados:list, transicoes:list,inicial):
    estados_inuteis = [est for est in estados]
    estados_inuteis.remove(inicial)

    for transicao in transicoes:
        estadoInicial, estadoFinal, simbTransicao = transicao.split(",")
        if estadoFinal in estados_inuteis:
            estados_inuteis.remove(estadoFinal)

    for inutil in estados_inuteis:
        estados.remove(inutil)
        for transicao in transicoes:
            if inutil in transicao:
                transicoes.remove(transicao)


def automato_view(request):
    if request.method == 'POST':
        form = AutomatoForm(request.POST, request.FILES)
        if form.is_valid():
            # Verifique se o arquivo foi enviado
            arquivo_txt = request.FILES.get('arquivo_txt')

            if arquivo_txt:
                # Processar o arquivo de texto
                dados_arquivo = arquivo_txt.read().decode('utf-8')
                linhas = dados_arquivo.strip().splitlines()

                # Inicializa as variáveis
                alfabeto, estados, inicial, finais, transicoes = None, None, None, None, []
                
                # Processa cada linha
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
                # Extrai os dados do formulário e os processa
                alfabeto = form.cleaned_data['alfabeto'].strip().split(',')  # Obtém o alfabeto e o separa em uma lista
                estados = form.cleaned_data['estados'].strip().split(',')  # Obtém os estados e os separa em uma lista
                inicial = form.cleaned_data['inicial'].strip()  # Estado inicial
                finais = form.cleaned_data['finais'].strip().split(',')  # Estados finais, separados em uma lista
                transicoes = [t.strip() for t in form.cleaned_data['transicoes'].split('\n')] # Transições, separadas e limpas


            validade, mensagem = validar_entrada(alfabeto, estados, inicial, finais, transicoes)

            if validade == False:
                return render(request, 'tfm\home.html', {'form': form,'mensagem':mensagem}) #


            remove_estado_inutil(estados, transicoes,inicial)

            # Cria todas as combinações possíveis de pares de estados e inverte cada tupla
            tuplasEstados = [tuple(tupla) for tupla in combinations(estados, 2)]

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
            grupos = []  # Lista para armazenar os grupos de equivalência
            for tupla in repetidos:
                encontrado = False
                for grupo in grupos:
                    # Verifica se algum elemento da tupla já está no grupo
                    if any(elem in grupo for elem in tupla):
                        grupo.update(tupla)  # Atualiza o grupo com os novos elementos
                        encontrado = True
                        break
                if not encontrado:
                    grupos.append(set(tupla))  # Cria um novo grupo com a tupla atual
            repetidos = []

            for grupo in grupos:
                uniao = set()
                for tupla in grupo:
                    uniao.update(tupla)
                uniao = list(uniao)
                if uniao[0].isdigit(): 
                    uniao = sorted(map(int, uniao))
                    uniao = list(map(str, uniao))
                else:
                    uniao = sorted(uniao)
                if inicial in uniao:
                    inicial = ''.join(uniao)
                repetidos.append(uniao)
            # Remove pares de uniaoEstados que tenham elementos já unidos na lista "uniao"
            remover = []
            for grupo in repetidos:
                for element in grupo:
                    for estado in uniaoEstados:
                        if element in estado:
                            if not estado in remover: 
                                remover.append(estado)

            for tupla in remover:
                uniaoEstados.remove(tupla)
            
            # Adiciona o conjunto unido de estados em uniaoEstados
            if repetidos:
                for grupo in repetidos:
                    uniaoEstados.append(grupo)

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
                        for estadoMinimizado in afdMinimizada:
                        # Verifica se o estado final da transição faz parte do estado minimizado atual
                            if estadoFinalTransicao in estadoMinimizado:
                            # Cria uma nova transição no formato "estadoInicial,estadoMinimizado,caracterTransicao"
                                novaTrasicao = estadoInicial + "," + estadoMinimizado + "," + caracterTransicao
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
                
            transicoesDict = {}
            for transicao in novasTrasicaos:
                estadoInicialTransicao, estadoFinalTransicao, caracterTransicao = transicao.split(',')
                    
                # Verifica se o estado inicial já existe no dicionário
                if estadoInicialTransicao not in transicoesDict:
                    transicoesDict[estadoInicialTransicao] = {}  # Cria um dicionário vazio para o estado inicial    
                # Adiciona a transição ao dicionário
                transicoesDict[estadoInicialTransicao][caracterTransicao] = estadoFinalTransicao   
            # Cria a imagem da AFD
            automata = DFA(afdMinimizada, alfabeto, transicoesDict, inicial, novoEstadosFinais)
            automata.view("tfm\\static\\imagem\\AFD_MIN")
            # Renderiza a página de resultado com o contexto atualizado]
            return render(request, 'tfm\\automato_result.html', context)
    else:
        form = AutomatoForm()
    
    return render(request, 'tfm\home.html', {'form': form})
 