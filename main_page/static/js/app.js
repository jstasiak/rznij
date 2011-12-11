 $(document).ready(function() {
    if(!window.console)
        window.console = {};

    var functions = ['log', 'dir', 'warn'];
    for(var index in functions) {
        var name = functions[index];
        if(!window.console[name]) {
            window.console[name] = function() {};
        }
    }

    socket = io.connect(null, { transports: ['flashsocket', 'xhr-polling'] });
    socket.on('connect', function() {
        console.log('connected');
    });

    socket.on('disconnect', function() {
        console.log('disconnected');
    });

    socket.on('reconnecting', function() {
        console.log('reconnecting');
    });

    socket.on('reconnect', function() {
        console.log('reconnected');
    });

    socket.on('error', function(e) {
        console.log('error: ' + e);
    });

    socket.on('message', function(message) {
        console.log('received:');
        console.dir(message);
    });

    var check_shortcut = function() {
        var element = $('#shortcut');
        var text = element.val();
        if (text) {
            console.log(text);
            socket.emit('shortcut_availability', text, function(response) {
                if(response.available) {
                    element.removeClass('error');
                }
                else {
                    element.addClass('error');
                }

                console.log('skrot ' + text + ' jest ' + (response.available ? 'dostepny' : 'niedostepny'));
            });
        }
        else {
            element.removeClass('error');
            console.log('tekst jest pusty, bedzie wylosowany');
        }
    };

    $('#shortcut').keyup(check_shortcut);

    var check_url = function() {
        var element = $('#url');
        var text = element.val();

        if(text) {
            element.removeClass('error');
        }
        else {
            element.addClass('error');
        }
    };

    $('#url').keyup(check_url);


    var submit = function() {
        if($('#url').hasClass('error')) {
            $('#url').focus();
            return false;
        }

        if($('#shortcut').hasClass('error')) {
            $('#shortcut').focus();
            return false;
        }

        var url = $('#url').val();
        var shortcut = $('#shortcut').val();

        socket.emit('create_shortcut', { shortcut: shortcut, url: url }, function(response) {
            if(response.success) {
                $('#shortcut_url').val(response['shortcut_url']).select().focus();
                $('#url').val('').removeClass('error');
                $('#shortcut').val('').removeClass('error');

            }
            else {
                alert('Wystapil blad: ' + response.message);
            }
        });

        return false;
    };

    $('#shortcut_form').submit(submit);

});


