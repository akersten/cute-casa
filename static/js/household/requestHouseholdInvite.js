if (!$('#selectHouseholdModal').length) {
    alert("requestHouseholdInvite.js is being included on the wrong page. It should only be used on household select.");
}


function showRequestHouseholdInvite() {
    // Show a modal dialog for the user to request a household invitation.
    var dialog = $('#selectHouseholdModal');

    dialog.modal('show');
}


// Don't send a request for every keystroke - wait until user is probably done typing.
var rhiRequestsInFlight = 0;
var rhiRequestDelay = 400;

function rhiTypeAhead() {
    // oninput handler for the household name field in the request invite screen. Populate the list of potential houses
    // with things we got from the server.


    var search = $('#inputHouseholdSearch').val();
    if (search && search.length > 0) {
        rhiRequestsInFlight++;
        setTimeout(rhiMaybeRequest, rhiRequestDelay);
    }
}

function rhiMaybeRequest() {
    rhiRequestsInFlight--;

    if (rhiRequestsInFlight != 0) {
        return;
    }

    var search = $('#inputHouseholdSearch').val();
    if (search && search.length > 0) {
        $.ajax({
            url: '/household/search/' + search,
            success: function (a, b) {
                alert(a);
            }
        });
    }
}

function rhiReturnedValues() {
    var shl = $('#selectHouseholdList');
    shl.append($('<a>').attr('href','#').attr('class','list-group-item').append(
       $('<h3>').append('HOUSEBALLLL')
    ));

}