/**
 * JS that runs on every page.
 **/



$(document).ready(function() {

    // Find any cwxs-match-heights and match them.
    var maxHeight = 0;
    $('.cwxs-match-height').each(function () {
        if ($(this).height() > maxHeight) {
            maxHeight = $(this).height();
        }
    });
    $('.cwxs-match-height').each(function () {
        $(this).css("height", maxHeight);
    });

});



