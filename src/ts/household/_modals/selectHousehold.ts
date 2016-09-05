/// <reference path="../../../../static/js/jquery.d.ts" />

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
        setTimeout(rhiSearch, rhiRequestDelay);
    } else {
        $('#selectHouseholdList').html('');
    }
}

function rhiSearch() {
    // Called as a setTimeout, perform a search on the given string if we are the last callback coming back from typing
    // within a certain period of time (e.g. make only one request to the server even if the user types rapidly).
    rhiRequestsInFlight--;

    if (rhiRequestsInFlight != 0) {
        return;
    }

    var search = $('#inputHouseholdSearch').val();
    // TODO: Since this search gets injected directly into the URL, prohibit characters like /, ?, and #

    if (search && search.length > 0) {
        $.ajax({
            url: '/household/search/' + search,
            success: function (a, b) {
                var list = $('#selectHouseholdList');
                var results = a.result;
                list.html('');
                if (results.length === 0) {
                    list.html('<h4 class="text-center">Sorry, no households matched your search.</h4>');
                } else {
                    $.each(results, function(key, r) {
                        list.append($('<a>')
                            .attr('class', 'list-group-item').attr('href','/household/request/' + r.id)
                            .append($('<h4>').text(r.household_name)));
                            /*.attr('onclick', 'rhiMakeRequest(' + r.id + ');')
                                .append($('<h4>').text(r.household_name)));*/
                    });
                }
            }
        });
    }
}

function rhiMakeRequest(id) {
    // Send a request to join a specific household, and then refresh the page to show our flashed message.
    $.ajax({
        url: '/household/request/' + id,
        success: function (a) {
            location.reload();
        }
        // TODO: Handle failure gracefully, here and everywhere we use ajax
    })
}