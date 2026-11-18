
#Integrantes:
#GIULLIANA MAISTRO BRASOLIN (RM: 569381) 
#LARA DOS SANTOS CÂNDIDO ALVES (RM: 573827) 
#MIKAELLA MIRELA DOS SANTOS LUCINDO (RM: 573775) 


class Registro:
    def __init__(self, id_, titulo, categoria, descricao="", requisitos="", local=""):
        self.id = id_
        self.titulo = titulo
        self.categoria = categoria
        self.descricao = descricao
        self.requisitos = requisitos
        self.local = local

    def __str__(self):
        return (
            f"[{self.id}] {self.titulo} | Categoria: {self.categoria}\n"
            f"     Descrição : {self.descricao or '-'}\n"
            f"     Requisitos: {self.requisitos or '-'}\n"
            f"     Local     : {self.local or '-'}"
        )


class No:
    def __init__(self, registro):
        self.registro = registro
        self.proximo = None


class ListaEncadeada:
    def __init__(self):
        self.inicio = None
        self.fim = None
        self.tamanho = 0

    def esta_vazia(self):
        return self.inicio is None

    def inserir(self, registro):
        novo = No(registro)
        if self.inicio is None:
            self.inicio = novo
            self.fim = novo
        else:
            self.fim.proximo = novo
            self.fim = novo
        self.tamanho += 1

    def percorrer(self):
        atual = self.inicio
        while atual is not None:
            yield atual.registro
            atual = atual.proximo

    def buscar_por_id(self, id_):
        atual = self.inicio
        while atual is not None:
            if atual.registro.id == id_:
                return atual.registro
            atual = atual.proximo
        return None

    def pesquisar(self, atributo, termo):
        resultado = ListaEncadeada()
        termo = termo.strip().casefold()
        atual = self.inicio
        while atual is not None:
            valor = str(getattr(atual.registro, atributo)).casefold()
            if termo in valor:
                resultado.inserir(atual.registro)
            atual = atual.proximo
        return resultado

    def remover(self, id_):
        anterior = None
        atual = self.inicio
        while atual is not None:
            if atual.registro.id == id_:
                if anterior is None:
                    self.inicio = atual.proximo
                else:
                    anterior.proximo = atual.proximo
                if atual is self.fim:
                    self.fim = anterior
                self.tamanho -= 1
                return True
            anterior = atual
            atual = atual.proximo
        return False

    def atualizar(self, id_, **campos):
        registro = self.buscar_por_id(id_)
        if registro is None:
            return False
        for nome, valor in campos.items():
            setattr(registro, nome, valor)
        return True

    def contar_por_categoria(self):
        contagem = ListaEncadeada()
        for reg in self.percorrer():
            chave = reg.categoria.casefold()
            atual = contagem.inicio
            achou = False
            while atual is not None:
                if atual.registro[0].casefold() == chave:
                    atual.registro[1] += 1
                    achou = True
                    break
                atual = atual.proximo
            if not achou:
                contagem.inserir([reg.categoria, 1])
        return contagem

    def ordenar(self, atributo="titulo"):
        self.inicio = self._merge_sort(self.inicio, atributo)
        self.fim = None
        atual = self.inicio
        while atual is not None:
            self.fim = atual
            atual = atual.proximo

    @staticmethod
    def _chave(registro, atributo):
        valor = getattr(registro, atributo)
        return valor if isinstance(valor, int) else str(valor).casefold()

    def _merge_sort(self, cabeca, atributo):
        if cabeca is None or cabeca.proximo is None:
            return cabeca
        lento, rapido = cabeca, cabeca.proximo
        while rapido is not None and rapido.proximo is not None:
            lento = lento.proximo
            rapido = rapido.proximo.proximo
        meio = lento.proximo
        lento.proximo = None
        esquerda = self._merge_sort(cabeca, atributo)
        direita = self._merge_sort(meio, atributo)
        return self._intercalar(esquerda, direita, atributo)

    def _intercalar(self, a, b, atributo):
        ficticio = No(None)
        cauda = ficticio
        while a is not None and b is not None:
            if self._chave(a.registro, atributo) <= self._chave(b.registro, atributo):
                cauda.proximo = a
                a = a.proximo
            else:
                cauda.proximo = b
                b = b.proximo
            cauda = cauda.proximo
        cauda.proximo = a if a is not None else b
        return ficticio.proximo


def ler_id(texto):
    texto = texto.strip()
    if not texto.isdigit():
        return None
    valor = int(texto)
    return valor if valor > 0 else None


def texto_valido(texto):
    return texto is not None and texto.strip() != ""


class CitizenAssist:
    def __init__(self):
        self.lista = ListaEncadeada()

    def cadastrar(self, id_texto, titulo, categoria, descricao="", requisitos="", local=""):
        id_ = ler_id(id_texto)
        if id_ is None:
            return False, "ID inválido: informe um número inteiro positivo."
        if not texto_valido(titulo) or not texto_valido(categoria):
            return False, "Título e categoria são obrigatórios."
        if self.lista.buscar_por_id(id_) is not None:
            return False, f"ID {id_} já existe. Use outro identificador."
        self.lista.inserir(
            Registro(id_, titulo.strip(), categoria.strip(),
                     descricao.strip(), requisitos.strip(), local.strip())
        )
        return True, f"Registro {id_} cadastrado com sucesso."

    def consultar(self, id_texto):
        if self.lista.esta_vazia():
            return None, "A lista está vazia."
        id_ = ler_id(id_texto)
        if id_ is None:
            return None, "ID inválido: informe um número inteiro positivo."
        reg = self.lista.buscar_por_id(id_)
        if reg is None:
            return None, f"Nenhum registro encontrado com ID {id_}."
        return reg, "Registro encontrado."

    def pesquisar(self, atributo, termo):
        if self.lista.esta_vazia():
            return None, "A lista está vazia."
        if atributo not in ("titulo", "categoria"):
            return None, "Atributo de pesquisa inválido."
        if not texto_valido(termo):
            return None, "Digite um termo de pesquisa."
        achados = self.lista.pesquisar(atributo, termo)
        if achados.esta_vazia():
            return None, f"Nenhum resultado para '{termo.strip()}'."
        return achados, f"{achados.tamanho} resultado(s) encontrado(s)."

    def atualizar(self, id_texto, titulo=None, categoria=None,
                  descricao=None, requisitos=None, local=None):
        if self.lista.esta_vazia():
            return False, "A lista está vazia."
        id_ = ler_id(id_texto)
        if id_ is None:
            return False, "ID inválido: informe um número inteiro positivo."
        campos = {
            "titulo": titulo, "categoria": categoria, "descricao": descricao,
            "requisitos": requisitos, "local": local,
        }
        campos = {k: v.strip() for k, v in campos.items() if texto_valido(v)}
        if not self.lista.atualizar(id_, **campos):
            return False, f"Nenhum registro encontrado com ID {id_}."
        return True, f"Registro {id_} atualizado."

    def excluir(self, id_texto):
        if self.lista.esta_vazia():
            return False, "A lista está vazia."
        id_ = ler_id(id_texto)
        if id_ is None:
            return False, "ID inválido: informe um número inteiro positivo."
        if self.lista.remover(id_):
            return True, f"Registro {id_} excluído."
        return False, f"Nenhum registro encontrado com ID {id_}."

    def ordenar(self, atributo):
        if self.lista.esta_vazia():
            return False, "A lista está vazia."
        if atributo not in ("id", "titulo", "categoria"):
            return False, "Critério de ordenação inválido."
        self.lista.ordenar(atributo)
        return True, f"Lista ordenada por {atributo} (Merge Sort)."


def mostrar_lista(lista, titulo="Registros"):
    print(f"\n--- {titulo} ({lista.tamanho}) ---")
    for reg in lista.percorrer():
        print(reg)


def menu():
    app = CitizenAssist()
    while True:
        print("\n===== Citizen Assist AI - Documentação e Cidadania =====")
        print("1 - Cadastrar registro")
        print("2 - Consultar por ID")
        print("3 - Pesquisar (título ou categoria)")
        print("4 - Atualizar registro")
        print("5 - Excluir registro")
        print("6 - Ordenar e exibir")
        print("7 - Análise (indicadores)")
        print("0 - Encerrar")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            ok, msg = app.cadastrar(
                input("ID (inteiro positivo): "), input("Título: "),
                input("Categoria: "), input("Descrição: "),
                input("Requisitos: "), input("Local: "))
            print(msg)

        elif opcao == "2":
            reg, msg = app.consultar(input("ID: "))
            print(msg)
            if reg:
                print(reg)

        elif opcao == "3":
            esc = input("Pesquisar por (1) título ou (2) categoria: ").strip()
            if esc not in ("1", "2"):
                print("Opção inválida.")
                continue
            atributo = "titulo" if esc == "1" else "categoria"
            achados, msg = app.pesquisar(atributo, input("Termo: "))
            print(msg)
            if achados:
                mostrar_lista(achados, "Resultado da pesquisa")

        elif opcao == "4":
            id_texto = input("ID do registro a atualizar: ")
            print("(Deixe em branco para manter o valor atual)")
            ok, msg = app.atualizar(
                id_texto, input("Novo título: "), input("Nova categoria: "),
                input("Nova descrição: "), input("Novos requisitos: "),
                input("Novo local: "))
            print(msg)

        elif opcao == "5":
            ok, msg = app.excluir(input("ID do registro a excluir: "))
            print(msg)

        elif opcao == "6":
            esc = input("Ordenar por (1) ID, (2) título ou (3) categoria: ").strip()
            atributo = {"1": "id", "2": "titulo", "3": "categoria"}.get(esc)
            if atributo is None:
                print("Opção inválida.")
                continue
            ok, msg = app.ordenar(atributo)
            print(msg)
            if ok:
                mostrar_lista(app.lista, f"Ordenados por {atributo}")

        elif opcao == "7":
            if app.lista.esta_vazia():
                print("A lista está vazia.")
                continue
            print(f"\nTotal de registros: {app.lista.tamanho}")
            print("Quantidade por categoria:")
            for categoria, qtd in app.lista.contar_por_categoria().percorrer():
                print(f"  - {categoria}: {qtd}")

        elif opcao == "0":
            print("Encerrando. Até logo!")
            break

        else:
            print("Opção inválida. Escolha um número do menu.")


if __name__ == "__main__":
    menu()
