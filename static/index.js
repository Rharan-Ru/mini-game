const loggedUser = JSON.parse(document.getElementById('user_id').textContent)
const username = JSON.parse(document.getElementById('username').textContent);

var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
var chatSocket = new WebSocket(ws_scheme + '://' + window.location.host + "/ws/game/");

chatSocket.onmessage = function(e) {
    console.log(loggedUser)
    const data = JSON.parse(e.data);
    if (data.sala_id){
        const sala_id = data.sala_id;
        console.log(sala_id);
        if (data.users_list.includes(loggedUser)) {
            window.location.pathname = sala_id + '/';
        }
    };

}


chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};

var filas = [];

function sendUser(fila) {
    if (fila) {
        chatSocket.send(JSON.stringify({
            'user_id': loggedUser,
        }));

        $('.contador').html('<h2 class="text-center m-0 p-2 text-white" ></h2>');
        $('.exclude_fila').css({'visibility': 'visible'});
        $('.sender_fila').css({'visibility': 'hidden'});

        var myVar = setInterval(myTimer, 1000);
        filas.push(myVar);
        var i = 1
        function myTimer() {
            $('.contador').html('<h2 class="text-center m-0 p-2 text-white" >' + i + '</h2>');
            i += 1;
            console.log(i);
        };

    }
    else {
        console.log('tudo certo');
        chatSocket.send(JSON.stringify({
            'sair_fila': loggedUser,
        }));
        $('.contador').html('');
        $('.exclude_fila').css({'visibility': 'hidden'});
        $('.sender_fila').css({'visibility': 'visible'});
        filas.forEach(clearInterval);
    }
}
