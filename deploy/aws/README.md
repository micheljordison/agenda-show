# Deploy AWS: git clone + Docker Compose na EC2

O deploy é feito diretamente em uma EC2 Linux: clonar o repositório, configurar o ambiente, construir as imagens e iniciar os serviços com Docker Compose. Não exige ECR, ECS ou pipeline AWS.

## O que foi preparado

- Imagens de produção: frontend Quasar compilado servido pelo Nginx e API FastAPI, ambos sem root.
- Compose de produção independente, sem volumes de código, servidor de desenvolvimento ou Supabase Studio.
- `/api` servido no mesmo domínio do frontend; suporte a acesso direto às rotas da SPA.
- Validação das configurações de produção, documentação da API desabilitada e migrations/bootstrap separados do início do servidor.
- Reinício automático, verificações de saúde e rotação dos logs Docker.
- PostgreSQL no Docker na mesma EC2, com volume persistente; HTTPS opcional com Caddy.

O Compose original continua sendo de desenvolvimento. Não combine `docker-compose.yml` com os arquivos de produção.

## 1. Preparar a EC2

Instalar Git, Docker Engine e o plugin Docker Compose v2. Habilitar o serviço Docker no boot e reservar espaço em disco para builds, imagens, logs e banco local. O build do frontend consome memória além daquela usada pela aplicação em execução; dimensionar a instância conforme medições da carga.

Para o HTTPS opcional incluído, apontar o domínio para o IP público estável da EC2 e liberar portas TCP 80/443 no security group. Restringir SSH 22 ao IP administrativo ou usar SSM. Não liberar 4050, 4080, 4100 ou 5432 para a Internet. O exemplo de ambiente publica HTTP em 0.0.0.0:8080. Liberar TCP 8080 no security group apenas para os clientes desejados; acessar http://IP_DA_EC2:8080. HTTPS não é necessário para iniciar este ambiente.

O Caddy precisa alcançar a Internet para emissão/renovação dos certificados. Se já existe proxy HTTPS ou ALB, omitir o complemento HTTPS e encaminhar tráfego ao frontend na porta 8080. Para ALB externo à máquina, definir `HTTP_BIND_ADDRESS=0.0.0.0` e permitir 8080 somente a partir do security group do ALB.

## 2. Clonar e configurar

Substituir a URL abaixo pela URL real do repositório (não foi fornecida):

```sh
git clone URL_DO_REPOSITORIO agenda
cd agenda
cp .env.production.example .env.production
chmod 600 .env.production
```

Editar `.env.production` antes de continuar:

- Manter `COMPOSE_PROJECT_NAME=agenda-production` entre releases: isso mantém a identidade dos volumes.
- Definir `JWT_SECRET_KEY` aleatória com pelo menos 32 caracteres e `INITIAL_MASTER_PASSWORD` aleatória com pelo menos 16. Por exemplo, gerar cada segredo separadamente com `openssl rand -hex 32`.
- `APP_DOMAIN` só é usado caso o complemento HTTPS seja habilitado futuramente.
- Manter `BACKEND_CORS_ORIGINS` vazio para frontend e API no mesmo domínio.
- Definir as credenciais PostgreSQL abaixo. Nunca versionar `.env.production`.

### PostgreSQL na própria EC2

O PostgreSQL já está incluído em `docker-compose.production.yml`. Definir apenas `POSTGRES_USER`, `POSTGRES_PASSWORD` e `POSTGRES_DB` no ambiente. O Compose monta a URL automaticamente, usando `database` como endereço interno; não configurar `DATABASE_URL` no `.env.production`:

```dotenv
DATABASE_URL=postgresql+psycopg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@database:5432/${POSTGRES_DB}?connect_timeout=5
```

Senha hexadecimal aleatória evita caracteres especiais na URL. Outras senhas exigem codificação URL na `DATABASE_URL`, mas o valor original em `POSTGRES_PASSWORD`. O banco fica sem porta no host e persiste no volume `production_postgres_data`. Mudar as variáveis `POSTGRES_*` não altera credenciais de um volume já inicializado: a rotação deve ser feita também no PostgreSQL.

## 3. Selecionar os arquivos Compose

Executar na raiz do repositório, usando Bash. A função abaixo usa PostgreSQL no Docker e HTTP, sem Caddy:

```sh
dc() {
  docker compose --env-file .env.production \
    -f docker-compose.production.yml "$@"
}
```

Para HTTPS futuramente, configurar `APP_DOMAIN` e adicionar `-f docker-compose.https.yml` antes de `"$@"`. Recriar essa função ao abrir uma nova sessão. Os comandos a seguir usam essa mesma seleção, inclusive para backup e rollback.

## 4. Primeira instalação

```sh
export RELEASE_TAG=$(git rev-parse --short=12 HEAD)
dc config --quiet
dc build --pull
```

Iniciar apenas o banco e aguardar ficar saudável:

```sh
dc up -d --wait database
```

Executar migrations e bootstrap uma única vez, na sequência. Parar se qualquer comando falhar:

```sh
dc run --rm --no-deps backend alembic upgrade head
dc run --rm --no-deps backend python -m app.bootstrap
```

Remover o valor de `INITIAL_MASTER_PASSWORD` de `.env.production` depois do bootstrap. O administrador já foi persistido no banco; essa senha não precisa ficar no container permanente. O bootstrap não troca a senha de um username existente.

```sh
dc up -d --no-build --wait
dc ps
curl --fail http://127.0.0.1:8080/api/ready
curl --fail http://IP_DA_EC2:8080/api/ready
```

Validar login, calendário, criação/edição de compromissos e atualização direta de `/login`. Se houver falha, consultar `dc logs --tail=100 backend frontend` e, com HTTPS local, `dc logs --tail=100 proxy`.

`/health` verifica apenas o processo. `/api/ready` retorna 503 quando não consegue consultar a tabela de usuários. Esse endpoint não substitui a confirmação de que todas as migrations foram aplicadas. `up --wait` verifica saúde dos containers; o teste HTTP final verifica também a conexão com o banco e o proxy.

## 5. Atualizar

Antes da atualização, anotar a tag atualmente implantada e fazer backup. Guardar as imagens anteriores; não executar limpeza de imagens usadas para rollback.

```sh
git status --short
git pull --ff-only
export RELEASE_TAG=$(git rev-parse --short=12 HEAD)
dc build --pull
```

Não continuar com alterações locais inesperadas ou build falhando. Fazer backup antes da migração. Para banco local, criar um dump no host:

```sh
mkdir -p backups
chmod 700 backups
umask 077
dc exec -T database sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "backups/agenda-$(date +%Y%m%d-%H%M%S).dump"
```

Conferir o resultado do comando e copiar os backups para armazenamento separado da EC2. Testar a restauração em banco descartável; manter arquivos apenas no disco da instância não protege contra a perda dela.

O procedimento abaixo tem uma breve janela de indisponibilidade e evita a API atendendo enquanto o schema é alterado:

```sh
dc stop frontend backend
dc run --rm --no-deps backend alembic upgrade head
dc up -d --no-build --force-recreate --wait
curl --fail http://IP_DA_EC2:8080/api/ready
```

Se a migration falhar, interromper a sequência e analisar os logs antes de subir a aplicação. Não executar deploys em paralelo. O `--force-recreate` também reinicia proxies da composição, evitando upstreams antigos após a troca dos containers; não remove volumes. Repetir o smoke test funcional depois do update.

## 6. Rollback e persistência

Se o schema continuar compatível com a versão anterior, selecionar a tag de imagem anterior e recriar os serviços **sem build**:

```sh
export RELEASE_TAG=TAG_ANTERIOR
dc up -d --no-build --force-recreate --wait
```

Esse comando pressupõe que as duas imagens anteriores ainda existem localmente e que a configuração Compose é compatível. Se a release também mudou a infraestrutura/configuração, restaurar os arquivos versionados daquela release de forma controlada, preservando `.env.production` e o nome do projeto. Não fazer downgrade destrutivo automaticamente; restaurar backup requer um procedimento próprio e pode perder gravações posteriores ao backup.

Não usar `docker compose down -v` em produção: remove os volumes de dados e certificados. Para parar os serviços mantendo os dados, usar `dc stop` ou `dc down` sem `-v`. Uma EC2 única não oferece failover automático.

## Segurança do acesso ao Docker

Neste deploy, administrar Docker pela sessão SSH da EC2, autenticada com chave privada. Manter o daemon no socket local; não habilitar acesso TCP público nas portas 2375/2376 nem montar `/var/run/docker.sock` nos containers. Uma variável `DOCKER_TOKEN` no `.env` não protege o daemon: Docker não a usa para autenticação.

O usuário com acesso ao Docker tem privilégios elevados sobre o host. Restringir o acesso SSH e guardar a chave privada fora do repositório. Os arquivos Compose de produção não publicam a porta do backend ou do PostgreSQL e não montam o socket Docker. Essas configurações não substituem a verificação do daemon e do security group na EC2.

O token da aplicação é separado: `JWT_SECRET_KEY` assina os tokens emitidos após o login. Usar um segredo aleatório exclusivo de produção e mantê-lo no servidor, nunca em variáveis `VITE_*` ou no JavaScript público. Alterar essa chave invalida os tokens de sessão anteriores.

Referência: [proteção do acesso ao Docker por SSH ou TLS](https://docs.docker.com/engine/security/protect-access/).

## Limites da validação

As imagens de produção foram construídas em Docker Linux com Python 3.12/Node 22. Os 20 testes do backend passaram também no container. Em um banco PostgreSQL 16 isolado, passaram as duas migrations, bootstrap, login, consulta do usuário e criação/edição/listagem de compromissos através do Nginx. Também foram verificados health/readiness, rota `/login`, bloqueio de chamadas sem autenticação, documentação da API desabilitada e execução de frontend/backend sem root. A configuração Nginx passou em `nginx -t`.

Ainda é necessário concluir a validação de persistência após recriação dos containers, HTTPS no domínio real e restauração de backup, além de migrations sobre banco preexistente quando aplicável. Executar scan das imagens e atualizar dependências vulneráveis: o projeto contém versões antigas e esta preparação não inclui uma auditoria completa. As imagens base usam tags e as dependências transitivas Python não possuem lock completo; fixar digests/lock após homologação melhora a reprodutibilidade. A integração Passlib/bcrypt emite um aviso de versão, embora o bootstrap e o login tenham funcionado nos testes.

A pasta recebida não contém `.git`; não foi possível verificar remoto ou histórico, nem criar commit. Nenhum recurso foi criado ou publicado na AWS.

## Referências

- [Security groups da EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-security-groups.html)
- [HTTPS automático do Caddy](https://caddyserver.com/docs/automatic-https)

