/**
 * Created by Ali.NET on 6/8/2021.
 */

var number_fields = [
    '.fieldBox.field-personnel_id div',
    '.fieldBox.field-basic_salary div',
    '.fieldBox.field-overtime_working div',
    '.fieldBox.field-insurance div',
    '.fieldBox.field-tax div',
    '.fieldBox.field-gross_salary div',
    '.fieldBox.field-deductions_sum div',
    '.fieldBox.field-salary_net div',
];

$( document ).ready(function() {
    function format_number_fields(item) {
        $(item).toArray().forEach(function(elem) {
            elem = $(elem);
            elem.text(format_number(elem));
        })
    }
    number_fields.forEach(format_number_fields)
});

