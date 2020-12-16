function start_loader() {
    if (document.getElementById('inputGroupFile01').value) {
        document.getElementById('result_layer').style.width = null;
        document.getElementById('result_layer').src = '/static/loader.gif';
    }
}

function load_data() {
    if (localStorage.getItem('data')) {
        let json = JSON.parse(localStorage.getItem('data'));
        document.getElementById('max_persons').value = json['max_persons'];
        document.getElementById('max_persons').placeholder = json['max_persons'];
        document.getElementById('message').value = json['message'];
        document.getElementById('message').placeholder = json['message'];
    } else {
        let json = {
            'max_persons': 10,
            'message': "__max__ personnes maximums dans le studio, merci de respecter les distances de sécurité. Vous êtes __actuel__ personnes actuellement dans la salle."
        };
        localStorage.setItem('data', JSON.stringify(json));
        load_data();
    }
}

function save_data() {
    let message;
    if (document.getElementById('message').value !== '') {
        message = document.getElementById('message').value;
    } else {
        message = "__max__ personnes maximums dans le studio, merci de respecter les distances de sécurité. Vous êtes __actuel__ personnes actuellement dans la salle."
    }

    let max;
    if (document.getElementById('max_persons').value !== '') {
        max = document.getElementById('max_persons').value;
    } else {
        let json = JSON.parse(localStorage.getItem('data'));
        max = json['max_persons'];
    }

    let json = {
        'max_persons': max,
        'message': message
    };
    localStorage.setItem('data', JSON.stringify(json));
}


async function extractFramesFromVideo(videoUrl, fps = 25) {
    return new Promise(async (resolve) => {

        // fully download it first (no buffering):
        let videoBlob = await fetch(videoUrl).then(r => r.blob());
        let videoObjectUrl = URL.createObjectURL(videoBlob);
        let video = document.createElement("video");

        let seekResolve;
        video.addEventListener('seeked', async function() {
            if(seekResolve) seekResolve();
        });

        video.src = videoObjectUrl;

        while((video.duration === Infinity || isNaN(video.duration)) && video.readyState < 2) {
            await new Promise(r => setTimeout(r, 1000));
            video.currentTime = 10000000*Math.random();
        }
        let duration = video.duration;

        let canvas = document.createElement('canvas');
        let context = canvas.getContext('2d');
        let [w, h] = [video.videoWidth, video.videoHeight];
        canvas.width =  w;
        canvas.height = h;

        let frames = [];
        let interval = 1 / fps;
        let currentTime = 0;

        while(currentTime < duration) {
            video.currentTime = currentTime;
            await new Promise(r => seekResolve=r);

            context.drawImage(video, 0, 0, w, h);
            let base64ImageData = canvas.toDataURL();
            frames.push(base64ImageData);
            process_picture(base64ImageData);
            currentTime += interval;
        }
        resolve(frames);
    });
}

async function start_processing() {
    let frames = await extractFramesFromVideo("http://techslides.com/demos/sample-videos/small.mp4", 1);
    console.log(frames);
}

function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function process_picture(frame) {
    $.ajax({
        type: "POST",
        url: "processing",
        data: { csrfmiddlewaretoken: getCookie('csrftoken'), frame: frame },
        success: function(data) {
            document.getElementById('result_layer').src = data;
        },
        failure: function(data) {
            alert('Got an error dude');
        }
    })
}