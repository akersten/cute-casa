////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Configuration...
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
const BACKGROUND_COLOR = '#eaeaea';
const BORDER_COLOR = '#e4e4e4';
const HIGHLIGHT_COLOR = '#f1f1f1';
const BORDER_WIDTH = 4;

const WALL_COLOR_DARK = '#333333';
const WALL_COLOR_MEDIUM = '#555555';
const WALL_COLOR_LIGHT = '#777777';
const WALL_THICKNESS = 3;

const GRID_COLOR = '#';
const GRID_WIDTH = 2;
const GRID_SPACING = 24;

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Object definitions...
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

/**
 * Something in the world is drawable, so everything should inherit from this.
 */
function Drawable() {

}

Drawable.prototype = {
    draw: function (ctx, offX, offY) {
        alert("Inherit the draw function...");
    },
    mousemoveHandler: function () {
        alert("Inherit the mousemove function...");
    },
    mousedownHandler: function (evt) {
        alert("Inherit the mousedown function...");
    },
    mouseupHandler: function (evt) {
        alert("Inherit the mouseup function...")
    }
};


/**
 * A room is a container/"layer" for walls and other household objects.
 */
function Room() {
    this.walls = [];
}
Room.prototype = Drawable;
Room.prototype.constructor = Room;


/**
 * A wall has a start and endpoint, and fill in-between.
 */
function Wall(colA, rowA, colB, rowB) {
    this.endpointA = {c: colA, r: rowA, moving: false};
    this.endpointB = {c: colB, r: rowB, moving: false};
    this.draw = function (ctx, offX, offY) {
        // Upper-left corners of each endpoint.
        var aX = this.endpointA.c * GRID_SPACING - offX;
        var aY = this.endpointA.r * GRID_SPACING - offY;
        var bX = this.endpointB.c * GRID_SPACING - offX;
        var bY = this.endpointB.r * GRID_SPACING - offY;

        ctx.lineWidth = WALL_THICKNESS;


        // Draw lines connecting the two endpoints.
        ctx.strokeStyle = WALL_COLOR_MEDIUM;
        ctx.beginPath();
        ctx.moveTo(aX, aY);
        ctx.lineTo(bX, bY);
        ctx.lineTo(bX + GRID_SPACING, bY);
        ctx.lineTo(aX + GRID_SPACING, aY);
        ctx.lineTo(aX + GRID_SPACING, aY + GRID_SPACING);
        ctx.lineTo(bX + GRID_SPACING, bY + GRID_SPACING);
        ctx.lineTo(bX, bY + GRID_SPACING);
        ctx.lineTo(aX, aY + GRID_SPACING);
        ctx.stroke();


        // Draw handles on each endpoint. Fill in with a color if they're being dragged.
        ctx.fillStyle = WALL_COLOR_LIGHT;
        //TODO

        ctx.strokeStyle = WALL_COLOR_DARK;
        ctx.strokeRect(aX, aY, GRID_SPACING, GRID_SPACING);
        ctx.strokeRect(bX, bY, GRID_SPACING, GRID_SPACING);


    };

    this.mousemoveHandler = function () {
        // Turn cursor if we're over a handle.
        if (mouseCol == this.endpointA.c && mouseRow == this.endpointA.r) {
            setCursorGrab();
        } else if (mouseCol == this.endpointB.c && mouseRow == this.endpointB.r) {
            setCursorGrab();
        } else {
            setCursorDefault();
        }

        // If we're moving, keep the endpoint locations updated.
        if (this.endpointA.moving) {
            this.endpointA.r = mouseRow;
            this.endpointA.c = mouseCol;
        }
        if (this.endpointB.moving) {
            this.endpointB.r = mouseRow;
            this.endpointB.c = mouseCol;
        }
    };

    this.mousedownHandler = function (evt) {

        switch (evt.which) {
            case 1:
                // Check if there was a click in a handle - if so, set its moving property.
                if (mouseCol == this.endpointA.c && mouseRow == this.endpointA.r) {

                    this.endpointA.moving = true;
                } else if (mouseCol == this.endpointB.c && mouseRow == this.endpointB.r) {
                    this.endpointB.moving = true;
                }
                break;
            default:
                break;
        }
    };

    this.mouseupHandler = function (evt) {
        switch (evt.which) {
            case 1:
                // No matter where the click was, we are no longer moving.
                this.endpointA.moving = false;
                this.endpointB.moving = false;
                break;
            default:
                break;
        }
    };
}
Wall.prototype = Drawable;
Wall.prototype.constructor = Wall;

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

// All of the objects in the world.
var worldObjects = [];

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

    // Draw gridlines
    c.strokeStyle = GRID_COLOR;
    c.lineWidth = GRID_WIDTH;

    for (var i = 0; i < height; i += GRID_SPACING) {
        c.strokeRect(0, i - (worldY % GRID_SPACING), width, GRID_WIDTH);
    }

    for (var i = 0; i < width; i += GRID_SPACING) {
        c.strokeRect(i - (worldX % GRID_SPACING), 0, GRID_WIDTH, height);
    }

    // Draw all of the drawable objects.
    for (var i = 0; i < worldObjects.length; i++) {
        worldObjects[i].draw(c, worldX, worldY);
    }
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

    // Propogate mouse movement events to all world objects...
    for (var i = 0; i < worldObjects.length; i++) {
        worldObjects[i].mousemoveHandler();
    }

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

    // Propogate mousedown events to all world objects...
    for (var i = 0; i < worldObjects.length; i++) {
        worldObjects[i].mousedownHandler(e);
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

    // Propogate mouseup events to all world objects...
    for (var i = 0; i < worldObjects.length; i++) {
        worldObjects[i].mouseupHandler(e);
    }
}

// Register listeners
$('#floorplanCanvas').on('mousemove', mouseMoveListener);
$('#floorplanCanvas').on('mousedown', mouseDownListener);
$('#floorplanCanvas').on('mouseup', mouseUpListener);
$('#floorplanCanvas').on('contextmenu', function () {
    return false; // Disable context menu on canvas for RMB dragging
});

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Utility functions
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

/**
 * Sets the cursor to a grabby cursor on the canvas.
 */
function setCursorGrab() {
    $('#floorplanCanvas').css('cursor', 'move');
}

/**
 * Sets the cursor to the default cursor on the canvas.
 */
function setCursorDefault() {
    $('#floorplanCanvas').css('cursor', 'default');
}

//
// Debug functions
//

function addWall() {

    var w = new Wall(1, 1, 5, 1);

    worldObjects.push(w);
}