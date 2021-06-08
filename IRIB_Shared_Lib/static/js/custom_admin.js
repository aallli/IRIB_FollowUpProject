/**
 * Created by Ali.NET on 6/26/2020.
 */
if (!String.prototype.format) {
    String.prototype.format = function () {
        var args = arguments;
        return this.replace(/{(\d+)}/g, function (match, number) {
            return typeof args[number] != 'undefined'
                ? args[number]
                : match
                ;
        });
    };
}

if (!$) {
    $ = django.jQuery;
}

function format_number(element) {
    return parseInt($(element).text()).toLocaleString('fa-IR');
}


