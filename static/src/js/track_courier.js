/** @odoo-module **/
import { jsonrpc } from "@web/core/network/rpc_service";

$(".confirm_track_do").click(function () {
    var tracking_number = $('.tracking-number-input').val();
    if(!tracking_number) {alert("Enter Tracking Number");}
    jsonrpc("/dev_courier_track", { 'do_no': tracking_number, }).then(function(res){
         if(res){
             $('.dev-tracking-container').removeClass('d-none');
             $('.customer-courier-status').text(res.status)
             $('.customer-courier-sender').text(res.sender_name)
             $('.customer-courier-receiver').text(res.receiver_name)
             $('.customer-courier-delivery-date').text(res.delivery_date)
             $('.dev-none-tracking-container').addClass('d-none');
            }
        if(!res){
            $('.dev-tracking-container').addClass('d-none');
            $('.dev-none-tracking-container').removeClass('d-none');
            }
    });

});

//});