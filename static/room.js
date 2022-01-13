const roomPK = JSON.parse(document.getElementById('room_pk').textContent);
const username = JSON.parse(document.getElementById('username').textContent);

var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
var chatSocket = new WebSocket(ws_scheme + '://' + window.location.host + "/ws/game/" + roomPK + "/");
var filas = [];


// Messages received from websocket
chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    // If game is ended show a modal to winner and loser player
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

    // Receive Log and change hp
    if (data.log) {
        if (data.selected != username){
            $('#chat-log').prepend('<p class="m-1 p-1" >'+ data.log +'</p>');
        } else {
            $('#chat-log').prepend('<p class="m-1 p-1" >'+ data.log +'</p>');
        };

        $('.hp_'+data.selected).css({'width': data.hp+'%'});
        chatSocket.send(JSON.stringify({
            'hp': [data.hp, data.selected],
        }));
    };

    // Receive selected user, add attack painel to selected user and start turn time
    if (data.selected) {
        if (data.selected == username){
            $('.'+username).html('<i class="bi bi-caret-right-fill m-0 p-0 col-6" onclick="attack(this.id)"> Basic attack</i><i class="bi bi-caret-right-fill m-0 p-0 col-6"> Block attack </i>')
            var myVar = setInterval(myTimer, 1000);
            var i = 15
            filas.push(myVar);
            // Start time down to selected user do an action / finish timer if user is not selected
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
        } else {
            $('.'+username).html('');
        }
    }
}
// ------------------------------------------------------------------------------------------------------------------

// Close chatsocket and finish all timedown
chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
    filas.forEach(clearInterval);
};
// ------------------------------------------------------------------------------------------------------------------

// If user reload a page or disconnect from match he is redirected to home page and lose the game
window.onbeforeunload = function() {
        // Send exit message to websocket
        chatSocket.send(JSON.stringify({
                'saiu': username,
            }));

        filas.forEach(clearInterval);
        window.setTimeout(function () {
            window.location = '/';
        }, 0);
        window.onbeforeunload = null; // necessary to prevent infinite loop, that kills your browser
    }
// ------------------------------------------------------------------------------------------------------------------

// Functions to send data to websocket from frontend
// Atack function
function attack(user) {
    chatSocket.send(JSON.stringify({
        'atk': username,
    }));
    filas.forEach(clearInterval);
}
// ------------------------------------------------------------------------------------------------------------------
