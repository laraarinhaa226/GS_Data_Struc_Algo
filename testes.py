from citizen_assist import CitizenAssist

resultados = []


def carregar_exemplos(app):
    exemplos = [
        ("3", "Emissão de RG", "Documentação", "Primeira e segunda via do RG.",
         "Certidão de nascimento ou casamento; comprovante de residência", "Poupatempo Sé"),
        ("1", "Título de eleitor", "Cidadania", "Cadastro e regularização eleitoral.",
         "Documento com foto; comprovante de residência", "Cartório Eleitoral"),
        ("5", "Bolsa Família", "Assistência Social", "Inscrição no CadÚnico.",
         "CPF; comprovante de renda familiar", "CRAS do bairro"),
        ("2", "Segunda via de CPF", "Documentação", "Regularização do CPF.",
         "Documento com foto", "Receita Federal"),
        ("4", "Carteira de Trabalho Digital", "Cidadania", "Emissão pelo app.",
         "CPF e dados pessoais", "Aplicativo Carteira de Trabalho Digital"),
    ]
    return sum(1 for e in exemplos if app.cadastrar(*e)[0])


def verificar(nome, entrada, esperado, observado):
    ok = esperado == observado
    resultados.append((nome, entrada, esperado, observado, ok))


def ids(lista):
    return [r.id for r in lista.percorrer()]


def titulos(lista):
    return [r.titulo for r in lista.percorrer()]


app = CitizenAssist()
verificar("Consultar com lista vazia", "consultar('1')", "A lista está vazia.", app.consultar("1")[1])
verificar("Pesquisar com lista vazia", "pesquisar('titulo','rg')", "A lista está vazia.", app.pesquisar("titulo", "rg")[1])
verificar("Excluir com lista vazia", "excluir('1')", "A lista está vazia.", app.excluir("1")[1])
verificar("Atualizar com lista vazia", "atualizar('1', titulo='x')", "A lista está vazia.", app.atualizar("1", titulo="x")[1])
verificar("Ordenar com lista vazia", "ordenar('titulo')", "A lista está vazia.", app.ordenar("titulo")[1])

verificar("Carregar 5 exemplos", "carregar_exemplos()", 5, carregar_exemplos(app))
verificar("Tamanho após exemplos", "lista.tamanho", 5, app.lista.tamanho)
ok, _ = app.cadastrar("6", "Certidão de nascimento", "Documentação", "2ª via", "RG", "Cartório")
verificar("Cadastro válido", "cadastrar('6', ...)", True, ok)
verificar("Tamanho após cadastro", "lista.tamanho", 6, app.lista.tamanho)

reg, _ = app.consultar("3")
verificar("Consulta por ID existente", "consultar('3')", "Emissão de RG", reg.titulo if reg else None)

achados, _ = app.pesquisar("categoria", "documentação")
verificar("Pesquisa por categoria (ignora caixa)", "pesquisar('categoria','documentação')",
          [3, 2, 6], ids(achados) if achados else None)
achados, _ = app.pesquisar("titulo", "cpf")
verificar("Pesquisa por título (substring)", "pesquisar('titulo','cpf')",
          [2], ids(achados) if achados else None)

app.atualizar("3", local="Poupatempo Itaquera")
verificar("Atualização válida", "atualizar('3', local=...)", "Poupatempo Itaquera", app.consultar("3")[0].local)
app.atualizar("3", titulo="   ")
verificar("Atualização com campo em branco mantém valor", "atualizar('3', titulo='   ')",
          "Emissão de RG", app.consultar("3")[0].titulo)

app.ordenar("id")
verificar("Ordenar por ID", "ordenar('id')", [1, 2, 3, 4, 5, 6], ids(app.lista))
app.ordenar("titulo")
verificar("Ordenar por título", "ordenar('titulo')",
          ["Bolsa Família", "Carteira de Trabalho Digital", "Certidão de nascimento",
           "Emissão de RG", "Segunda via de CPF", "Título de eleitor"], titulos(app.lista))
app.ordenar("categoria")
cats = [r.categoria for r in app.lista.percorrer()]
verificar("Ordenar por categoria", "ordenar('categoria')",
          ["Assistência Social", "Cidadania", "Cidadania", "Documentação", "Documentação", "Documentação"], cats)
verificar("Ordenação estável (empate preserva ordem anterior)", "categoria 'Cidadania'",
          ["Carteira de Trabalho Digital", "Título de eleitor"],
          [r.titulo for r in app.lista.percorrer() if r.categoria == "Cidadania"])
app.ordenar("id")
app.cadastrar("7", "Novo", "Teste")
verificar("Inserir após ordenar (ponteiro fim correto)", "ordenar + cadastrar('7')",
          [1, 2, 3, 4, 5, 6, 7], ids(app.lista))

contagem = {c: q for c, q in app.lista.contar_por_categoria().percorrer()}
verificar("Quantidade por categoria", "contar_por_categoria()",
          {"Documentação": 3, "Cidadania": 2, "Assistência Social": 1, "Teste": 1}, contagem)

app.excluir("1")
verificar("Excluir primeiro nó", "excluir('1')", [2, 3, 4, 5, 6, 7], ids(app.lista))
app.excluir("4")
verificar("Excluir nó do meio", "excluir('4')", [2, 3, 5, 6, 7], ids(app.lista))
app.excluir("7")
verificar("Excluir último nó", "excluir('7')", [2, 3, 5, 6], ids(app.lista))
app.cadastrar("8", "Depois da exclusão", "Teste")
verificar("Inserir após excluir último (fim correto)", "cadastrar('8')", [2, 3, 5, 6, 8], ids(app.lista))
for i in ("2", "3", "5", "6", "8"):
    app.excluir(i)
verificar("Esvaziar a lista", "excluir de todos", True, app.lista.esta_vazia())
verificar("Tamanho zero após esvaziar", "lista.tamanho", 0, app.lista.tamanho)
app.cadastrar("1", "Reinserção", "Teste")
verificar("Cadastrar em lista que foi esvaziada", "cadastrar('1')", [1], ids(app.lista))

app = CitizenAssist()
carregar_exemplos(app)
verificar("ID duplicado", "cadastrar('1', ...)", (False, "ID 1 já existe. Use outro identificador."),
          app.cadastrar("1", "Outro", "Cat"))
verificar("ID não numérico", "cadastrar('abc', ...)", False, app.cadastrar("abc", "T", "C")[0])
verificar("ID negativo", "cadastrar('-5', ...)", False, app.cadastrar("-5", "T", "C")[0])
verificar("ID zero", "cadastrar('0', ...)", False, app.cadastrar("0", "T", "C")[0])
verificar("ID vazio", "cadastrar('', ...)", False, app.cadastrar("", "T", "C")[0])
verificar("Título vazio", "cadastrar('9','', 'C')", False, app.cadastrar("9", "  ", "C")[0])
verificar("Categoria vazia", "cadastrar('9','T','')", False, app.cadastrar("9", "T", "")[0])
verificar("Consultar ID inexistente", "consultar('999')", "Nenhum registro encontrado com ID 999.", app.consultar("999")[1])
verificar("Consultar ID inválido", "consultar('xyz')", "ID inválido: informe um número inteiro positivo.", app.consultar("xyz")[1])
verificar("Pesquisa sem resultado", "pesquisar('titulo','zzz')", "Nenhum resultado para 'zzz'.", app.pesquisar("titulo", "zzz")[1])
verificar("Pesquisa com termo vazio", "pesquisar('titulo','')", "Digite um termo de pesquisa.", app.pesquisar("titulo", "")[1])
verificar("Pesquisa com atributo inválido", "pesquisar('cor','x')", "Atributo de pesquisa inválido.", app.pesquisar("cor", "x")[1])
verificar("Atualizar ID inexistente", "atualizar('999', titulo='x')", False, app.atualizar("999", titulo="x")[0])
verificar("Excluir ID inexistente", "excluir('999')", False, app.excluir("999")[0])
verificar("Ordenação com critério inválido", "ordenar('cor')", False, app.ordenar("cor")[0])
verificar("Tamanho intacto após operações inválidas", "lista.tamanho", 5, app.lista.tamanho)

print(f"{'#':>2} | {'Teste':<52} | {'Resultado'}")
print("-" * 75)
for i, (nome, entrada, esperado, observado, ok) in enumerate(resultados, 1):
    print(f"{i:>2} | {nome:<52} | {'PASSOU' if ok else 'FALHOU'}")
    if not ok:
        print(f"     entrada  : {entrada}")
        print(f"     esperado : {esperado}")
        print(f"     observado: {observado}")
total = len(resultados)
passou = sum(1 for r in resultados if r[4])
print("-" * 75)
print(f"{passou}/{total} testes passaram.")
raise SystemExit(0 if passou == total else 1)
