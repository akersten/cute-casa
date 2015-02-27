var canvas = document.getElementById('floorplanCanvas');
var c = canvas.getContext('2d');

/**
 * Event listener to keep canvas coordinate system syncrhonized with CSS coordinates on window resize.
 */
(function () {
    var canvas = $('#floorplanCanvas');

    initCanvas();
    function initCanvas() {
        window.addEventListener('resize', resizeCanvasWithWindow, false);
        resizeCanvasWithWindow();
    }

    function resizeCanvasWithWindow() {
        var w = $('#floorplanCanvasContainer').width();
        var h = $('#floorplanCanvasContainer').height();
        canvas.attr("width", w);
        canvas.attr("height", h);
        redraw();
    }
})();

/**
 * Drawing of canvas elements happens here.
 */
function redraw() {
    var width = canvas.clientWidth;
    var height = canvas.clientHeight;

    c.strokeStyle = 'blue';
    c.lineWidth = '5';

    c.strokeRect(width / 2 - 30, height / 2 - 25, 60, 50);
}
