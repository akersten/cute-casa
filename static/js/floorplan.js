/**
 * Configuration...
 */

const BORDER_COLOR = '#efefef';
const BORDER_WIDTH = 4;

const GRID_COLOR = '#';
const GRID_WIDTH = 2;
const GRID_SPACING = 16;

/**
 * Instance variables ;)
 */

var posX = 0; // Where are we in the world?
var posY = 0;
var mX = 0; // Mouse x and y.
var mY = 0;
/**
 * Canvas initialization...
 */

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


function mouseMoveListener(e) {
    var offset = $('#floorplanCanvas')[0].getBoundingClientRect();
    mX = e.clientX - offset.left;
    mY = e.clientY - offset.top;
    redraw();
}

$('#floorplanCanvas').on('mousemove', mouseMoveListener);




/**
 * Drawing of canvas elements happens here.
 */
function redraw() {
    var width = canvas.clientWidth;
    var height = canvas.clientHeight;

    // Draw a border around the canvas to make it look nice...
    c.strokeStyle = BORDER_COLOR;
    c.lineWidth = BORDER_WIDTH;
    c.strokeRect(0, 0, width, height);

    // Draw gridlines
    c.strokeStyle = GRID_COLOR;
    c.lineWidth = GRID_WIDTH;

    for (var i = 0; i < height; i += GRID_SPACING) {
        c.strokeRect(0, i + posY % GRID_SPACING, width, GRID_WIDTH);
    }

    for (var i = 0; i < width; i += GRID_SPACING) {
        c.strokeRect(i + posX % GRID_SPACING, 0, GRID_WIDTH, height);
    }

    c.strokeStyle="#ff0000";
    c.strokeRect(mX, mY, 10, 10);
}
