if (!$('#selectHouseholdModal').length) {
    alert("requestHouseholdInvite.js is being included on the wrong page. It should only be used on household select.");
}


function showRequestHouseholdInvite() {
    // Show a modal dialog for the user to request a household invitation.
    var dialog = $('#selectHouseholdModal');

    dialog.modal('show');
}