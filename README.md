# Django Channels Mini Game RPG☼

## About Project

<p>
  Olá, este é mais um projeto de estudo sobre websockets com Django Channels, é um jogo rpg baseado em turnos, esse projeto é interessante para compreender como websockets funcionam e como ele pode ser usado com Django para resolver problemas 
  como a sincronização ou processos assincronos de dados que precisam ser mostrados para o usuário em tempo real, como mensagens de conversas, notificações e processos em 
  segundo plano o que abre muitas possibilidades a serem exploradas.
</p>

### How Start The Project?

Primeiro de tudo vamos clonar este repositório
````
git clone https://github.com/Monke001/mini-game.git
cd mini-game
````
Agora instalamos as dependencias dentro do requimeremts.txt, mas primeiro ativamos nossa venv
````
python3 -m venv venv
cd venv/Scripts/activate
pip install -r requirements.txt
````
Então rodamos o projeto, recomendo trocar o superuser do projeto para ter acesso a page admin e também rodar os comandos makemigrations e migrate
````
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py createsuperuser
python3 manage.py runserver
````

### Features

<p>
  Algumas das features principais do projeto feitas foram:
</p>

- Sistema de level up, o jogador ganhar xp ao ganhar partidas.
- Um sistema simples de fila para jogadores procurarem partidas com outros jogadores.
- Sistema de turnos, em que tem um tempo limite para o usuário realizar uma ação, caso contrário o turno é passada adiante.
- Log da partida.

### The Future

<p>
  A ideia do projeto está usando um sistema monolítico de escalamento porque é um jogo simples de rpg mas se caso o projeto escalasse muito eu poderia refazer com uma arquitetura
  mais apropriada usando Microsservices e Event Driven Architecture, mas isso depende muito, no mais o MVT do Django suple as nossas nescessidades, mais adiante eu penso em colocar
  mais interação no jogo, fazendo salas de Chefes Globais, adicionando items mágicos para os jogadores droparem, adicionar dungeons e um modo para quatro jogadores batalharem.
  Infelizmente jogos demoram muito para criar e ficarem jogáveis sem bugs e problemas técnicos, então eu confesso esse projeto é muito ambicioso para mim, mas isso que o torna mais divertido de criar.
</p>

<hr />

#### Obrigado por estar aqui, eu nunca vou parar, vou ficar um pouco melhor a cada dia trazendo projetos cada vez mais interessantes.

<p align="center">
  <img src="https://jonchaisson.files.wordpress.com/2021/10/anime-writing.gif" width=70% />
</p>
