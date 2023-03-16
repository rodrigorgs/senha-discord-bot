# SenhaBot

Bot para Discord que informa ao usuário qual sua senha, obtida de uma planilha do Google Sheets.

Além disso, ele incorpora comandos de gerenciamento de filas de atendimento do [Classroom Bot](https://top.gg/bot/691945666896855072).

## Configurando o bot no Discord

To create a Discord bot on Discord's developer portal, follow these steps:

1. Go to the Discord developer portal at https://discord.com/developers/applications.
2. Click on the "New Application" button in the top right corner.
3. Enter a name for your application and click on the "Create" button.
4. Click on the "Bot" tab on the left side of the screen, then click on the "Add Bot" button.
5. Customize your bot's settings by giving it a username and uploading an avatar image.
6. Once you're satisfied with your bot's settings, click on the "Copy" button under "Token" to copy your bot's authentication token. This token will be used to connect your bot to Discord's API. Take note of this token, because it can only be displayed just after creation.

## Configurando o acesso do bot ao Google Drive

<https://gspread.readthedocs.io/en/latest/oauth2.html>

## Instalando dependências

```sh
pip -r requirements.txt
```

## Para rodar localmente

Crie um arquivo `config.sh` com as variáveis de ambiente. Exemplo:

```sh
export DISCORD_BOT_TOKEN=token-do-bot-do-discord
export DATABASE_URL='postgres://postgres:1234@localhost:5432/postgres'
export GOOGLE_SERVICE_ACCOUNT_JSON=$(cat <<-END
Cole aqui o JSON gerado pelo Google
}
END
)
```

Inicie os containers Docker (será criado um container para o banco de dados PostgreSQL):

```sh
docker-compose up --build
```

Aguarde aparecer a mensagem `I am online`.

## Convidando o bot para seu servidor

Primeiramente, crie um cargo **Teacher** no servidor, adicionando você próprio como membro. Apenas usuários com esse cargo podem executar comandos de administração do bot.

Então, acesse o link <https://discord.com/api/oauth2/authorize?client_id=NNN&permissions=11264&scope=bot>, substituindo `NNN` pelo Application ID do bot. Essa URL corresponde às permissões Read Messages/View Channels, Send Messages e Manage Messages.

To get your bot's application id on Discord's developer portal, follow these steps:

1. Go to the Discord developer portal at https://discord.com/developers/applications.
2. Click on the application that contains your bot.
3. Click on the "General Information" tab on the left side of the screen.
4. Scroll down until you see the "Application ID" section. Your bot's application id will be displayed here.
5. You can also copy the application id by clicking on the "Copy" button next to it.

## Criando a planilha de dados

Para usar o SenhaBot, você deve criar um documento do Google Sheets e **compartilhá-lo com a conta do SenhaBot** no Google, com **permissão de Editor**. Além disso, você digitar o seguinte comando no servidor:

```
?unibot set_spreadsheet_id <value>
```

Substituindo `<value>` pleo ID do documento. Esse ID é uma string alfanumérica que aparece na URL do documento, entre `/spreadsheets/d/` e `/edit`.

O documento deve ter uma planilha `STUDENTS`, incluindo ao menos as seguintes colunas:

- `STUDENT_ID`: número de matrícula do estudante
- `STUDENT_NAME`: nome do estudante
- `DISCORD_ID`: ID do estudante no Discord. É preenchido pelo bot.
- `INFO`: informações que o bot envia ao estudante que as solicitar, em privado, tipicamente senhas, notas de avaliações...
- `TEAM_ID` (opcional): identificador da equipe do estudante, tipicamente usado para trabalhos em grupo

Além disso, quando há trabalhos em equipe, deve-se criar uma planilha `TEAMS`, incluindo as seguintes colunas:

- `TEAM_ID`: ID do time; deve ser pré-preenchida com os números de 1 a 99
- colunas com nome iniciado por `ATTR_`: informações adicionais que as equipes podem preencher através do bot

## Usando o bot

Digite `?help` para obter ajuda sobre os comandos
