/**
 * Configuration...
 */

const BACKGROUND_COLOR = '#eaeaea';
const BORDER_COLOR = '#e4e4e4';
const HIGHLIGHT_COLOR = '#f1f1f1';
const BORDER_WIDTH = 4;

const GRID_COLOR = '#';
const GRID_WIDTH = 2;
const GRID_SPACING = 24;

/**
 * Instance variables ;)
 */
var posX = 0; // Where are we in the world?
var posY = 0;
var mX = 0; // Mouse x and y.
var mY = 0;
var lmX = 0; // Last mouse x and mouse y.
var lmY = 0;
var col = 0; // Mouse col and row in absolute terms
var row = 0;
var mb1 = false; // Mouse button states.
var mb2 = false;
var mb3 = false;

/**
 * Canvas initialization...
 */

var canvas = document.getElementById('floorplanCanvas');
var c = canvas.getContext('2d');


/**
 * Drawing of canvas elements happens here.
 */
function redraw() {
    var width = canvas.clientWidth;
    var height = canvas.clientHeight;

    c.fillStyle = BACKGROUND_COLOR;
    c.fillRect(0, 0, width, height);

    // Draw a border around the canvas to make it look nice...
    c.strokeStyle = BORDER_COLOR;
    c.lineWidth = BORDER_WIDTH;
    c.strokeRect(0, 0, width, height);

    // Fill current row and column
    c.fillStyle = HIGHLIGHT_COLOR;
    c.fillRect((mX + posX % GRID_SPACING), 0, GRID_SPACING, height);
    c.fillRect(0, (mY + posY % GRID_SPACING), width, GRID_SPACING);

    // Draw gridlines
    c.strokeStyle = GRID_COLOR;
    c.lineWidth = GRID_WIDTH;

    for (var i = 0; i < height; i += GRID_SPACING) {
        c.strokeRect(0, i - (posY % GRID_SPACING), width, GRID_WIDTH);
    }

    for (var i = 0; i < width; i += GRID_SPACING) {
        c.strokeRect(i - (posX % GRID_SPACING), 0, GRID_WIDTH, height);
    }
    c.strokeRect(mX, mY, 10, 10);
}

/**
 * Resolve the mouse position into row/col
 */
function resolveMouse() {
    return {
        row: Math.floor((mY + posY) / GRID_SPACING),
        col: Math.floor((mX + posX) / GRID_SPACING)
    };
}

//
// Event listeners and initialization follow.
//

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

    // Update mouse positions and calculate deltas
    lmX = mX;
    lmY = mY;
    mX = e.clientX - offset.left;
    mY = e.clientY - offset.top;
    var dX = mX - lmX;
    var dY = mY - lmY;

    if (mb3) {
        posX -= dX;
        posY -= dY;
    }

    var cr = resolveMouse();
    col = cr.col;
    row = cr.row;

    redraw();
}

function mouseDownListener(e) {
    switch (e.which) {
        case 1:
            mb1 = true;
            break;
        case 2:
            mb2 = true;
            break;
        case 3:
            mb3 = true;
            break;
    }
}

function mouseUpListener(e) {
    switch (e.which) {
        case 1:
            mb1 = false;
            break;
        case 2:
            mb2 = false;
            break;
        case 3:
            mb3 = false;
            break;
    }
}

$('#floorplanCanvas').on('mousemove', mouseMoveListener);
$('#floorplanCanvas').on('mousedown', mouseDownListener);
$('#floorplanCanvas').on('mouseup', mouseUpListener);
$('#floorplanCanvas').on('contextmenu', function () {
    return false;
});
