/**
 * Created by Ali.NET on 6/8/2021.
 */

var number_fields = [
    '.field-amount a',
    '.field-amount div div',
];

$( document ).ready(function() {
    function format_number_fields(item) {
        div = $(item);
        div.text(format_number(div));
    }
    number_fields.forEach(format_number_fields)
});

