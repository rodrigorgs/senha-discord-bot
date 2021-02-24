# SenhaDiscordBot

Bot para Discord que informa ao usuário qual sua senha, obtida de uma planilha do Google Sheets.

## Configurando o bot no Discord

<https://dev.to/p014ri5/making-and-deploying-discord-bot-with-python-4hep>

## Configurando o acesso do bot ao Google Drive

<https://gspread.readthedocs.io/en/latest/oauth2.html>

## Instalando dependências

```sh
pip -r requirements.txt
```

## Para rodar localmente

Exporte as variáveis de ambiente relevantes. Exemplo:

```sh
export DISCORD_BOT_TOKEN=token-do-bot-do-discord
```

Veja a lista completa de variáveis de ambiente no arquivo `bot.py`.

Então execute o bot:

```sh
python bot.py
```

Aguarde aparecer a mensagem `I am online`.

## Para rodar no Heroku

No plano gratuito, a aplicação dorme quando não está sendo usada, e demorada para ser iniciada. Para evitar que a aplicação durma, pode-se usar algum serviço como o https://uptimerobot.com/
