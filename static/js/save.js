window.onload = function() {

    //add constraints object
    var constraints = { audio: false,
                        video: false};

    //call getUserMedia, then the magic
    navigator.mediaDevices.getUserMedia(constraints).then(function(mediaStream){
        var video = document.querySelector('video');
        video.srcObject = mediaStream;
        video.play();
    }).catch(function(err){
        console.log("yikes, and err!" + err.message);
    });

}
