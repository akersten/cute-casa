if (!$('#createSharedBill').length) {
    alert("createSharedBill.js is being included on the wrong page. It should only be used on Shared Bills.");
}


function showCreateSharedBill() {
    // Show a modal dialog for the user to request a household invitation.
    var dialog = $('#createSharedBill');
    dialog.modal('show');
}