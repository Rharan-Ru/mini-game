const roomPK = JSON.parse(document.getElementById('room_pk').textContent);
const username = JSON.parse(document.getElementById('username').textContent);

var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
var chatSocket = new WebSocket(ws_scheme + '://' + window.location.host + "/ws/game/" + roomPK + "/");
var filas = [];

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    if (data.sair) {
        $('.live_modal').click();
        if (data.winner == username) {
            $('.modal-title').html('<p>Você Venceu!!</p>');
            $('.modal-body').html('<p>Parabens você ganhou!</p>');
            filas.forEach(clearInterval);
        }
        else {
            $('.modal-title').html('<p>Você Perdeu!!</p>');
            $('.modal-body').html('<p>Mais sorte da próxima vez!</p>');
            filas.forEach(clearInterval);
        }
    }

    if (data.selected != username){
        $('.vez').html('Vez de '+ data.selected);
    }
    else {
        $('.vez').html('Sua vez')
    };

    if (data.log) {
        const d = new Date();
        if (data.selected != username){
            $('#chat-log').prepend('<p class="m-1 p-1" >'+ data.log +'</p>');
        }
        else {
            $('#chat-log').prepend('<p class="m-1 p-1" >'+ data.log +'</p>');
        };

        var width_percent = $('.hp_'+data.selected).width() / $('.hp_'+data.selected).parent().width() * 100;
        var width_now = width_percent - data.dano;
        $('.hp_'+data.selected).css({'width': width_now+'%'});

        chatSocket.send(JSON.stringify({
            'hp': [width_now, data.selected],
        }));
    };

    if (data.selected) {
        if (data.selected == username){
//            $('.'+username).css({'display': 'flex'});
            $('.'+username).html('<i class="bi bi-caret-right-fill m-0 p-0 col-6" onclick="attack(this.id)"> Basic attack</i><i class="bi bi-caret-right-fill m-0 p-0 col-6"> Block attack </i>')
            var myVar = setInterval(myTimer, 1000);
            filas.push(myVar);
            var i = 15
            function myTimer() {
                $('.contador').html(i);
                console.log(i);
                chatSocket.send(JSON.stringify({
                    'cont': i,
                    'turn': data.selected,
                }));
                if (i === 0) {
                    filas.forEach(clearInterval);
                };
                i -= 1;
            };
            myTimer();
        }
        else {
//            $('.'+username).css({'display': 'none'});
            $('.'+username).html('');
        }
    }
}

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
    filas.forEach(clearInterval);
};

window.onbeforeunload = function() {
        chatSocket.send(JSON.stringify({
                'saiu': username,
            }));
        filas.forEach(clearInterval);
        window.setTimeout(function () {
            window.location = '/';
        }, 0);
        window.onbeforeunload = null; // necessary to prevent infinite loop, that kills your browser
    }

function attack(user) {
    chatSocket.send(JSON.stringify({
        'atk': username,
    }));
    filas.forEach(clearInterval);
}