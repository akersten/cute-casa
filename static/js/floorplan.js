////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Configuration...
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
const BACKGROUND_COLOR = '#eaeaea';
const BORDER_COLOR = '#e4e4e4';
const HIGHLIGHT_COLOR = '#f1f1f1';
const BORDER_WIDTH = 4;

const GRID_COLOR = '#';
const GRID_WIDTH = 2;
const GRID_SPACING = 24;

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Object definitions...
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Instance variables...
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Position - where is the viewport looking in absolute coordinates?
var worldX = 0;
var worldY = 0;

// Mouse position - x and y in viewport terms.
var mouseViewX = 0;
var mouseViewY = 0;

// Mouse row/col - in absolute coordinates.
var mouseCol = 0;
var mouseRow = 0;

// Mouse button states - true for down, false for up.
var mouse1 = false;
var mouse2 = false;
var mouse3 = false;

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Canvas initialization...
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
var canvas = document.getElementById('floorplanCanvas');
var c = canvas.getContext('2d');


/**
 * Draw canvas elements.
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
    c.fillRect((mouseViewX + worldX % GRID_SPACING), 0, GRID_SPACING, height);
    c.fillRect(0, (mouseViewY + worldY % GRID_SPACING), width, GRID_SPACING);

    // Draw gridlines
    c.strokeStyle = GRID_COLOR;
    c.lineWidth = GRID_WIDTH;

    for (var i = 0; i < height; i += GRID_SPACING) {
        c.strokeRect(0, i - (worldY % GRID_SPACING), width, GRID_WIDTH);
    }

    for (var i = 0; i < width; i += GRID_SPACING) {
        c.strokeRect(i - (worldX % GRID_SPACING), 0, GRID_WIDTH, height);
    }
    c.strokeRect(mouseViewX, mouseViewY, 10, 10);
}

/**
 * Resolve the mouse position into row/col.
 */
function resolveMouse() {
    return {
        row: Math.floor((mouseViewY + worldY) / GRID_SPACING),
        col: Math.floor((mouseViewX + worldX) / GRID_SPACING)
    };
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Event listeners and initialization...
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

/**
 * Keep canvas coordinate system syncrhonized with CSS coordinates on window resize.
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
 * Want to track where the mouse moved to update, also implements scroll-dragging.
 */
function mouseMoveListener(e) {
    var offset = $('#floorplanCanvas')[0].getBoundingClientRect();

    // Calculate current mouse position
    var newX = e.clientX - offset.left;
    var newY = e.clientY - offset.top;

    // Calculate deltas
    var dX = newX - mouseViewX;
    var dY = newY - mouseViewY;

    // Update global mouse position
    mouseViewX = newX;
    mouseViewY = newY;

    // Move viewport if scrolling
    if (mouse3) {
        worldX -= dX;
        worldY -= dY;
    }

    // Calculate and update column and row locations
    var cr = resolveMouse();
    mouseCol = cr.col;
    mouseRow = cr.row;

    redraw();
}

/**
 * Watch for mousedown events and set global flags.
 */
function mouseDownListener(e) {
    switch (e.which) {
        case 1:
            mouse1 = true;
            break;
        case 2:
            mouse2 = true;
            break;
        case 3:
            mouse3 = true;
            break;
    }
}

/**
 * Watch for mouseup events and set global flags.
 */
function mouseUpListener(e) {
    switch (e.which) {
        case 1:
            mouse1 = false;
            break;
        case 2:
            mouse2 = false;
            break;
        case 3:
            mouse3 = false;
            break;
    }
}

// Register listeners
$('#floorplanCanvas').on('mousemove', mouseMoveListener);
$('#floorplanCanvas').on('mousedown', mouseDownListener);
$('#floorplanCanvas').on('mouseup', mouseUpListener);
$('#floorplanCanvas').on('contextmenu', function () {
    return false; // Disable context menu on canvas for RMB dragging
});
