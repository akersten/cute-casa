/*
 * Initialization for floorplan - runs after layout and bringup.
 */


// Start by selecting the move tool
selectTool('moveTool');

$(document).ready(function(){
    // Add tabindex to the canvas so it can intercept key events
    $('#floorplanCanvas').attr("tabindex", '1');


    $('#floorplanCanvas').focus();
});