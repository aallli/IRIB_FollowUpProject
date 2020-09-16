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

var counter = 0;
var max_try = 20;
function bind_selector() {
    var dropdowns = document.querySelectorAll('[id^=id_followup_set-][id$=-actor]');
    if (!dropdowns || dropdowns.length == 0) {
        if (counter > max_try) return;
        setTimeout(bind_selector, 1000);
        return;
    }
    dropdowns.forEach(function (item, index) {
        var supervisor = document.querySelector('#followup_set-{0} .field-supervisor p'.format(index));
        if (!supervisor) return;
        item.onchange = function () {
            $.ajax({
                url: url,
                data: {
                    'pk': this.value,
                },
                success: function (data) {
                    supervisor.innerText = data ? data : '-';
                }
            });
        };
    })
}


bind_selector();


