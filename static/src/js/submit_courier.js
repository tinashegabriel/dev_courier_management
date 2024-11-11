/** @odoo-module **/
import { jsonrpc } from "@web/core/network/rpc_service";

$(".web_cr_submit_button").click(function () {
    var sender_name = $('.input_sender_name').val();
    var sender_mobile = $('.input_sender_mobile').val();
    var sender_email = $('.input_sender_email').val();
    var sender_street = $('.input_sender_street').val();
    var sender_street2 = $('.input_sender_street2').val();
    var sender_city = $('.input_sender_city').val();
    var sender_state_id = $('.input_sender_state_id').val();
    var sender_zip = $('.input_sender_zip').val();
    var sender_country_id = $('.input_sender_country_id_id').val();
    var receiver_name = $('.input_receiver_name').val();
    var receiver_mobile = $('.input_receiver_mobile').val();
    var receiver_email = $('.input_receiver_email').val();
    var receiver_street = $('.input_receiver_street').val();
    var receiver_street2 = $('.input_receiver_street2').val();
    var receiver_city = $('.input_receiver_city').val();
    var receiver_state_id = $('.input_receiver_state_id_id').val();
    var receiver_zip = $('.input_receiver_zip').val();
    var receiver_country_id = $('.input_receiver_country_id_id').val();
    var input_data_vals = {
    'sender_name': sender_name,
    'sender_mobile': sender_mobile,
    'sender_email': sender_email,
    'sender_street': sender_street,
    'sender_street2': sender_street2,
    'sender_city': sender_city,
    'sender_state_id': sender_state_id,
    'sender_zip': sender_zip,
    'sender_country_id': sender_country_id,
    'receiver_name': receiver_name,
    'receiver_mobile': receiver_mobile,
    'receiver_email': receiver_email,
    'receiver_street': receiver_street,
    'receiver_street2': receiver_street2,
    'receiver_city': receiver_city,
    'receiver_state_id': receiver_state_id,
    'receiver_zip': receiver_zip,
    'receiver_country_id': receiver_country_id,
    }

    jsonrpc("/guest_user_courier_submit", { 'input_data': input_data_vals, }).then(function(res){
         if(res){
            }
        if(!res){
            }
    });

});
//});