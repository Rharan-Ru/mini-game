const roomPK = JSON.parse(document.getElementById('room_pk').textContent);
const username = JSON.parse(document.getElementById('username').textContent);

var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
var chatSocket = new WebSocket(ws_scheme + '://' + window.location.host + "/ws/game/" + roomPK + "/");

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    if (data.sair) {
        if (data.winner == username) {
            $('.modal-title').html('<p>Você Venceu!!</p>');
            $('.modal-body').html('<p>Parabens você ganhou!</p>');
        }
        else {
            $('.modal-title').html('<p>Você Perdeu!!</p>');
            $('.modal-body').html('<p>Mais sorte da próxima vez!</p>');
        }

        $('.live_modal').click();
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
            $('#chat-log').prepend('<p class="m-1 p-1" > [ '+ d.toLocaleTimeString() +' ] Você causou '+ data.dano +' de dano</p>');
        }
        else {
            $('#chat-log').prepend('<p class="m-1 p-1" > [ '+ d.toLocaleTimeString() +' ] ' + data.log +'</p>');
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
        }
        else {
//            $('.'+username).css({'display': 'none'});
            $('.'+username).html('');
        }
    }
}

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};


function attack(user) {
    chatSocket.send(JSON.stringify({
        'atk': username,
    }));
}