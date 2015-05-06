////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// DOM integration
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
var toolNames = [
  "moveTool", "wallTool", "roomTool", "doorTool", "windowTool"
];

var currentTool = "none";

function selectTool(tool) {
    for (var i = 0; i < toolNames.length; i++) {
        $('#' + toolNames[i]).removeClass('btn-primary');
    }

    var t = $('#' + tool);
    currentTool = tool;
    t.addClass('btn-primary');
}

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
var GRID_SPACING = 24; // Can adjust to zoom in/out

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
        return true;
    },
    mouseupHandler: function (evt) {
        alert("Inherit the mouseup function...");
        return true;
    }
};


/**
 * A room is a container/"layer" for walls and other household objects.
 */
function Room() {
//    this.walls = [];
    this.roomId = -1; // A unique ID for this room within the world.

    this.roomName = "unnamed room";



    this.mousemoveHandler = function () {

    };

    this.mousedownHandler = function (evt) {
        return false;
    };

    this.mouseupHandler = function (evt) {
        return false;
    };

    this.draw = function(ctx, offX, offY) {

    };
}
Room.prototype = Drawable;
Room.prototype.constructor = Room;

Room.highestRoom = -1; // Highest numbered room ID

/**
 * A wall has a start and endpoint, and fill in-between.
 */
function Wall(colA, rowA, colB, rowB) {
    // A flag used in various graph traversals to mark the node (this wall). The searcher is responsible for resetting
    // these after a search. Example use of determining room membership.
    this.qtmark = false;


    this.wallId = -1; // A unique ID for this wall within the world

    this.roomMembership = []; // The room membership of this wall (an array of room IDs).


    this.endpointA = {c: colA, r: rowA, movingX: false, movingY: false};
    this.endpointB = {c: colB, r: rowB, movingX: false, movingY: false};
    this.draw = function (ctx, offX, offY) {
        // Upper-left corners of each endpoint.
        var aX = this.endpointA.c * GRID_SPACING - offX;
        var aY = this.endpointA.r * GRID_SPACING - offY;
        var bX = this.endpointB.c * GRID_SPACING - offX;
        var bY = this.endpointB.r * GRID_SPACING - offY;

        ctx.lineWidth = WALL_THICKNESS;


        // Draw a wall connecting the two endpoints. We want this wall to be of bounding thickness, so let's think about
        // this. The innermost and outermost pairs of verts won't have a line connecting them - we just want lines
        // between the middle-distance pairs of verts, to form the wall.
        ctx.fillStyle = WALL_COLOR_LIGHT;
        ctx.strokeStyle = WALL_COLOR_MEDIUM;


        // Find the quadrant that one endpoint is in relative to the other - this way we know which 2 verts need to be
        // connected with straight lines.
        if (aY > bY) {
            quadrant = aX > bX ? 1 : 2;
        } else {
            quadrant = aX > bX ? 4 : 3;
        }



        // Calculate middle endpoint positions.
        var mediumPoint1A = {x: 0, y: 0};
        var mediumPoint1B = {x: 0, y: 0};
        var mediumPoint2A = {x: 0, y: 0};
        var mediumPoint2B = {x: 0, y: 0};

        switch (quadrant) {
            case 1:
            case 3:
                mediumPoint1A.x = aX + GRID_SPACING;
                mediumPoint1A.y = aY;
                mediumPoint1B.x = bX + GRID_SPACING;
                mediumPoint1B.y = bY;

                mediumPoint2A.x = aX;
                mediumPoint2A.y = aY + GRID_SPACING;
                mediumPoint2B.x = bX;
                mediumPoint2B.y = bY + GRID_SPACING;
                break;
            case 2:
            case 4:
                mediumPoint1A.x = aX;
                mediumPoint1A.y = aY;
                mediumPoint1B.x = bX;
                mediumPoint1B.y = bY;

                mediumPoint2A.x = aX + GRID_SPACING;
                mediumPoint2A.y = aY + GRID_SPACING;
                mediumPoint2B.x = bX + GRID_SPACING;
                mediumPoint2B.y = bY + GRID_SPACING;
                break;
            default:

        }

        // Create the path between the medium points.
        ctx.beginPath();

        // Move to the first medium point, draw to its pair, draw to the second's pair, draw to the second..
        ctx.moveTo(mediumPoint1A.x, mediumPoint1A.y);
        ctx.lineTo(mediumPoint1B.x, mediumPoint1B.y);
        ctx.lineTo(mediumPoint2B.x, mediumPoint2B.y);
        ctx.lineTo(mediumPoint2A.x, mediumPoint2A.y);

        ctx.fill();
        ctx.stroke();

        // Draw handles on each endpoint, and feedback fill if being dragged.
        ctx.strokeStyle = WALL_COLOR_DARK;

        if (this.endpointA.movingX === true || this.endpointA.movingY === true) {
            ctx.fillStyle = BACKGROUND_COLOR;
        } else {
            ctx.fillStyle = WALL_COLOR_MEDIUM;
        }
        ctx.fillRect(aX, aY, GRID_SPACING, GRID_SPACING);
        ctx.strokeRect(aX, aY, GRID_SPACING, GRID_SPACING);

        if (this.endpointB.movingX === true || this.endpointB.movingY === true) {
            ctx.fillStyle = BACKGROUND_COLOR;
        } else {
            ctx.fillStyle = WALL_COLOR_MEDIUM;
        }

        ctx.fillRect(bX, bY, GRID_SPACING, GRID_SPACING);
        ctx.strokeRect(bX, bY, GRID_SPACING, GRID_SPACING);
    };

    this.mousemoveHandler = function () {
        // Turn cursor if we're over a handle and on an appropriate tool.
        if (currentTool === "moveTool") {
            if (mouseCol == this.endpointA.c && mouseRow == this.endpointA.r) {
                setCursorGrab();
            } else if (mouseCol == this.endpointB.c && mouseRow == this.endpointB.r) {
                setCursorGrab();
            }
        }

        // If we're moving, keep the endpoint locations updated.
        if (this.endpointA.movingX) {
            this.endpointA.c = mouseCol;
        }
        if (this.endpointA.movingY) {
            this.endpointA.r = mouseRow;
        }

        if (this.endpointB.movingX) {
            this.endpointB.c = mouseCol;
        }
        if (this.endpointB.movingY) {
            this.endpointB.r = mouseRow;
        }
    };

    this.mousedownHandler = function (evt) {

        switch (evt.which) {
            case 1:
                // Check if there was a click in a handle - if so, set its moving property.
                if (currentTool === "moveTool") {
                    if (mouseCol == this.endpointA.c && mouseRow == this.endpointA.r) {
                        this.endpointA.movingX = true;
                        this.endpointA.movingY = true;
                        return true;
                    } else if (mouseCol == this.endpointB.c && mouseRow == this.endpointB.r) {
                        this.endpointB.movingX = true;
                        this.endpointB.movingY = true;
                        return true;
                    }
                }

                break;
            default:
                break;
        }
        return false;
    };

    this.mouseupHandler = function (evt) {
        switch (evt.which) {
            case 1:
                // No matter where the click was, we are no longer moving.
                this.endpointA.movingX = false;
                this.endpointA.movingY = false;
                this.endpointB.movingX = false;
                this.endpointB.movingY = false;

                // Check for degenerate walls and remove them.
                var degenerate = false;

                // The first degenerate wall is one with zero length.
                if (this.endpointA.c == this.endpointB.c && this.endpointA.r == this.endpointB.r) {
                    removeWall(this);
                    degenerate = true;
                }

                // The second type of degenerate wall is one that completely overlaps another wall. Check against all
                // others (yep) and remove this one if need be.


                // Wall structures changed, check for room creation and destruction.
                if (degenerate) {
                    //recalculateRoomsD(this);

                    // TODO: still the case that destroying a partitioning wall will leave the surrounding 4 walls in a
                    // state where there is no interior room but the walls clearly constitute a room. Need to probably
                    // call a global recalculate here.

                    // Actually, the way we'll get around this is requiring all rooms to have endpoints matching on
                    // walls (so no T-intersections with a non-endpoint part of the wall).
                } else {
                    //recalculateRoomsC(this);
                }

                return true;
                break;
            default:
                break;
        }
        return false;
    };
}
Wall.prototype = Drawable;
Wall.prototype.constructor = Wall;

Wall.highestWall = -1; // The current highest-numbered wall in the world. If this is -1, figure out what the highest wall
                    // is and start counting from there.

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

    // Reset the cursor before letting objects change it.
    setCursorDefault();

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
    var consumed = false;
    for (var i = 0; i < worldObjects.length; i++) {
        consumed |= worldObjects[i].mousedownHandler(e);
    }

    if (consumed != true) {
        // Default mouse-down actions here.

        switch (e.which) {
            case 1:
                // Default action depends on which tool we have selected.

                if (currentTool === "wallTool") {
                    // Create a wall object with its first wall fixed, and its second endpoint set to moving.
                    var w = addWall(mouseCol, mouseRow, mouseCol, mouseRow);
                    w.endpointB.movingX = true;
                    w.endpointB.movingY = true;

                } else if (currentTool == "roomTool") {
                    // Create four walls, and set moving on a few of their endpoints.
                    var t = addWall(mouseCol, mouseRow, mouseCol, mouseRow);
                    var l = addWall(mouseCol, mouseRow, mouseCol, mouseRow);
                    var b = addWall(mouseCol, mouseRow, mouseCol, mouseRow);
                    var r = addWall(mouseCol, mouseRow, mouseCol, mouseRow);

                    t.endpointB.movingX = true;
                    l.endpointB.movingY = true;
                    b.endpointA.movingY = true;
                    b.endpointB.movingX = true;
                    b.endpointB.movingY = true;
                    r.endpointA.movingX = true;
                    r.endpointB.movingX = true;
                    r.endpointB.movingY = true;
                }

                break;
            case 2:
                break;
            case 3:
                break;

        }

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
    var consumed = false;
    for (var i = 0; i < worldObjects.length; i++) {
        consumed |= worldObjects[i].mouseupHandler(e);
    }

    if (consumed != true) {
        // Default mouse-up actions here.
    }
}

/**
 * Watch for mousewheel events.
 */
function mouseWheelListener(e) {
    var distance = e.originalEvent.wheelDelta || - e.originalEvent.detail;  // Stupid firefox, not only does it use a
                                                                            // different event, its deltas are also
                                                                            // negative... Woo browser interop!

    if (distance > 0) {
        zoomCanvas(1);
    } else {
        zoomCanvas(-1);
    }
}

// Register listeners
$('#floorplanCanvas').on('mousemove', mouseMoveListener);
$('#floorplanCanvas').on('mousedown', mouseDownListener);
$('#floorplanCanvas').on('mouseup', mouseUpListener);
$('#floorplanCanvas').on('mousewheel DOMMouseScroll', mouseWheelListener);
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

/**
 * Zoom in or out.
 */
function zoomCanvas(direction) {
    if (direction > 0) {
        GRID_SPACING = Math.min(32, GRID_SPACING + 1);
    } else {
        GRID_SPACING = Math.max(10, GRID_SPACING - 1);
    }

    redraw();
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// World modification functions, like wall addition and removal, and room creation and destruction
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
function addWall(cA, rA, cB, rB) {
    var w = new Wall(cA, rA, cB, rB);
    w.wallId = ++Wall.highestWall;
    worldObjects.push(w);
    console.log("Added a wall with id " + w.wallId);
    return w;
}

function removeWall(wall) {
    if (!wall instanceof Wall) {
        console.error("removeWall called on something that wasn't a wall.");
    }

    worldObjects.splice(worldObjects.indexOf(wall), 1);
}
