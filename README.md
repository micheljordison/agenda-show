# Sistema de Compromissos

Aplicacao web autenticada para gerenciamento de compromissos, com frontend em Quasar, backend em FastAPI e banco PostgreSQL.

## Portas

- Frontend: `4000`
- Backend: `4050`
- PostgreSQL: `4080`

## Arquitetura

```text
Usuario
  -> URL / Dominio
  -> Proxy / Servidor
  -> Frontend Quasar :4000
  -> Backend FastAPI :4050
  -> PostgreSQL :4080
```

## Organizacao

```text
backend/app
  apresentacao/controllers     Endpoints HTTP
  aplicacao/servicos           Regras de negocio e autorizacao
  aplicacao/helpers            Configuracao, seguranca e dependencias
  repositorio/db               Contexto de banco
  repositorio/modelos          Modelos SQLAlchemy
  repositorio/migrations       Migrations Alembic

frontend/src
  components                   Componentes reutilizaveis
  components/state             Componentes de estado
  pages                        Telas compostas
  services                     Cliente HTTP
  stores                       Estado da aplicacao
```

## Execucao local com Docker

1. Copie `.env.example` para `.env`.
2. Ajuste os valores de ambiente.
3. Suba os servicos:

```bash
docker compose up --build
```

4. Execute migrations:

```bash
docker compose exec backend alembic upgrade head
```

5. Acesse:

- Frontend: http://localhost:4000
- Backend: http://localhost:4050/docs

## Desenvolvimento e testes

As dependencias devem ser instaladas pelos containers. Nao e necessario instalar Python, Node ou pacotes do projeto na maquina local.

Subir a aplicacao:

```bash
docker compose up --build
```

No frontend, as dependencias ficam no volume Docker `frontend_node_modules`. Elas sao instaladas na primeira subida e reinstaladas apenas quando o `package.json` mudar.

Rodar migrations:

```bash
docker compose exec backend alembic upgrade head
```

Rodar testes do backend:

```bash
docker compose exec backend pytest
```

Gerar build do frontend dentro do container:

```bash
docker compose run --rm frontend npm run build
```

## Deploy

O `docker-compose.yml` acima e exclusivo de desenvolvimento. Para producao, use
as imagens com target `production` e o arquivo independente
`docker-compose.production.yml` em uma EC2,
com clone do repositorio e build local. O PostgreSQL roda no Docker na mesma instancia.

Consulte [o guia AWS](deploy/aws/README.md) para `git clone`, configuracao do banco,
HTTPS, primeira instalacao, atualizacoes, migrations, bootstrap e rollback.
O exemplo de ambiente esta em `.env.production.example`.

Nao exponha PostgreSQL, backend ou Supabase Studio publicamente. Execute migrations
uma vez por release e crie o administrador com `python -m app.bootstrap` antes de
iniciar o servico de producao. O frontend atende `/api` pelo mesmo endereco HTTP.

## Seguranca

- Senhas sao armazenadas com hash.
- Endpoints protegidos exigem usuario autenticado.
- Autorizacao e aplicada no backend.
- Usuario comum ve apenas compromissos vinculados.
- Usuario master ve todos os compromissos e pode desvincular qualquer usuario.
- Secrets devem ficar em variaveis de ambiente.
