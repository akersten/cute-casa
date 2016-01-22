/**
 * Created by akersten on 12/19/15.
 */
if (!$('#generateInvoiceModal').length) {
    alert("generateInvoice.js is being included on the wrong page. It should only be used on billing admin.");
}


function showGenerateInvoice() {
    // Show a modal dialog for the user to request a household invitation.
    var dialog = $('#generateInvoiceModal');

    dialog.modal('show');
}