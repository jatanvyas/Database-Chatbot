var resp;
var opt;

var $messages = $('.messages-content'),
i = 0;

$(window).load(function() {
  $messages.mCustomScrollbar();
});

function updateScrollbar() {
  $messages.mCustomScrollbar("update").mCustomScrollbar('scrollTo', 'bottom', {
    scrollInertia: 10,
    timeout: 0
  });
};

function insertMessage() {
  msg = $('.message-input').val();
  if ($.trim(msg) == '') {
    return false;
  };
  postData(msg);

  $('<div class="message message-personal">' + msg + '</div>').appendTo($('.mCSB_container')).addClass('new');
  $('.message-input').val(null);
  updateScrollbar();

  setTimeout(function() {
    fakeMessage();
  }, 1000);
};

$('.message-submit').click(function() {
  startDictation();
});

$(window).on('keydown', function(e) {
  if (e.which == 13) {
    insertMessage();
    return false;
  }
});

function fakeMessage() {
  if ($('.message-input').val() != '') {
    return false;
  }
  $('<div class="message loading new"><figure class="avatar"><img src="Avatar.png" /></figure><span></span></div>').appendTo($('.mCSB_container'));
  updateScrollbar();

  setTimeout(function() {
    $('.message.loading').remove();
    $('<div class="message new"><figure class="avatar"><img src="Avatar.png" /></figure>' + resp + '</div>').appendTo($('.mCSB_container')).addClass('new');
    var yo = new SpeechSynthesisUtterance(resp);
    window.speechSynthesis.speak(yo);
    updateScrollbar();
    i++;
  }, 4000);
}

function startDictation() {

    if (window.hasOwnProperty('webkitSpeechRecognition')) {

      var recognition = new webkitSpeechRecognition();

      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = "en-US";
      recognition.start();
      recognition.onresult = function(e) {
        document.getElementById('textbox').value = e.results[0][0].transcript;
        recognition.stop();
        insertMessage();
      };

      recognition.onerror = function(e) {
        recognition.stop();
      }
    }
  };

function postData(x){
    var obj = {"message":x}
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "http://localhost:5004/chat/", true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify(obj));

    xhr.onload = function() {
        var jsresp = JSON.parse(xhr.responseText);
        resp = jsresp.text;

        if(jsresp.option) {
            opt = jsresp.option;
            var ext = opt.split('.').pop();
            if(ext == "html" || ext == "csv" || ext == "xlsx"){                                  //its results table
                document.getElementById('res').src = opt;
                document.getElementById('res').src = document.getElementById('res').src;
            } else {                                            //its poster or graph
                var iframe = document.getElementById('res');
                var html = "<p style='text-align:center;'><img src=" + opt +"></p>";
                var doc = iframe.contentDocument || iframe.contentWindow.document;
                doc.body.innerHTML = html;
            }
        };
    };
};
