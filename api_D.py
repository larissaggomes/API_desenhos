from flask import Flask, Response, request, json, send_file
from flask_cors import CORS
import time
import os

# app = Flask(__name__, static_url_path='/static')
app = Flask(__name__)
cors = CORS(app)
DB = "dbdata.json"

# rota para acessar as imagem na api
@app.route('/imagens/<path:filename>')
def get_image(filename):
    # unindo o path das imagens com o nome da imagem
    image_path = f"data/imagens/{filename}"

    # retorna a imagem como um arquivo
    return send_file(image_path, mimetype='images/jpeg') # especifique o mimetype correto para sua imagem

def generateId():
    # pegando a data e hora em formato timestamp (migrosegundos)
    timestamp = time.time()
    # removendo o ponto que separa os segundos
    timestamp = str(timestamp).replace('.','')
    # retornado o valor
    return timestamp

#lista de produtos
@app.route('/internal')
def ler():
    try:
        with open(DB, "r") as arquivo:
            json_objeto = json.load(arquivo)
        return json_objeto
    except IOError:
        return [] 

#consultar(todos)
@app.route('/produtos', methods=['GET'])
def obter_produtos():
    args = request.args
    produtos = ler()

    # if args.get('filter'):
    #     if args.get('filter') == 'relatorio':
    #         for indice,produto in enumerate(produtos):
    #             if produto['estoque'] > produto['estoqueMinimo']:
    #                 del produtos[indice] 

    return Response(
        response=json.dumps(produtos), status=200,  mimetype="text/plain")
    
#consultar(por id)
@app.route('/produtos/<int:id>',methods=['GET'])
def obter_produto_por_id(id):
    res = ""
    resultado = ler()
    for produto in resultado:
        if int(produto["id"]) == int(id):
            res = produto
    
    return Response(
        response=json.dumps(res), status=200,  mimetype="text/plain")
          
        
#editar
@app.route('/produtos/<int:id>',methods=['PUT'])
def editar_produto_por_id(id):
    resultado = ler()
    for produto in resultado:
        if int(produto["id"]) == int(id):
            produto["nome"] = request.form.get('nome')
            produto["autor"] = request.form.get('autor') 
            produto["descricao"] =  request.form.get('descricao')
            produto["data"] = request.form.get('data')
            if 'imagem' in request.files:
                os.remove(f"data/imagens/{produto['imagem']}")
                produto["imagem"] = upload()

    json_objeto = json.dumps(resultado, indent=4)

    with open(DB, "w") as arquivo:
        arquivo.write(json_objeto)
        return Response(
            response=json.dumps(True), status=200, mimetype="text/plain"
        ) 
    
#criar 
@app.route('/produtos',methods=['POST'])    
def incluir_novo_produto():
    
    # pegando a lista de produtos do banco de dados
    produtos = ler()

    # pegando os dados do produtos que veio no body da requisição
    novo_produto = {
        'id': generateId(), #gerando e adicionado um novo id para produto
        'nome': request.form.get('nome'),
        'autor': request.form.get('autor'),
        'descricao': request.form.get('descricao'),
        'data': request.form.get('data'),
        'imagem': upload() # fazendo o upload e recebendo o path
    }

    # adicionado o novo produto na lista de produtos
    produtos.append(novo_produto)
    # convertendo a lista de produtos em objetos json
    json_objeto = json.dumps(produtos, indent=4)

    # abrindo o banco de dados no modo escrita(W)
    with open(DB, "w") as arquivo:
        # escrevendo no arquivo a lista de produtos
        arquivo.write(json_objeto)
    
    
    return Response(
        response=json.dumps(True), status=200,  mimetype="text/plain")
    
#excluir
@app.route('/produtos/<int:id>',methods=['DELETE'])
def excluir_produto(id):
    # pegando a lista de produtos do banco de dados
    # a partir do metodo ler
    produtos = ler()

    # fazendo um loop na lista de produtos
    for indice,produto in enumerate(produtos):

        # comparando se o id do banco é igual
        # ao id enviando pela reguisição
        if int(produto["id"]) == int(id):
            os.remove(f"data/imagens/{produto['imagem']}")
            # removendo o produto da lista a partir do indice (posição)
            del produtos[indice]

    # convertendo a lista de produtos em um objeto no formato texto
    json_objeto = json.dumps(produtos, indent=4)
    
    # abrindo o arquivo de banco de dados no modo escrita(W)
    with open(DB, "w") as arquivo:
        # escrevando o objeto json no arquivo
        arquivo.write(json_objeto)

        # retornado uma resposta para o frontend
        return Response(response=json.dumps(True), status=200,  mimetype="text/plain")
    
def upload():
    # criando variavel path com o caminho da pasta de imagens
    path = 'data/imagens/'

    # verificando se a pasta existe, caso não, criar a pasta
    if not os.path.exists(path):
        os.makedirs(path)

    # verificando se o arquivo chamado "imagem" esta presente nos arquivos da requisição
    if 'imagem' not in request.files:
        return 'Nenhum arquivo enviado'
    
    # salvando na variavel file o arquivo de imagem 
    file = request.files['imagem']
    split = file.filename.split('.') 
    ext = split[-1]
    name = f"{generateId()}.{ext}"

    # salvando o arquivo na pasta configurada em path + nome do arquivo de file.filename
    file.save(f"{path}{name}")

    # retornado o nome do arquivo
    return name

app.run(port=4000,host='localhost', debug=True)