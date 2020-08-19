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
function bind_selector(name) {
    var dropdown = document.getElementsByName('{0}_actor'.format(name));
    if (!dropdown || dropdown.length == 0) {
        if (counter > max_try) return;
        setTimeout(bind_selector, 1000, name);
        return;
    }
    dropdown = dropdown[0];

    var supervisor = document.querySelector('.fieldBox.field-box.field-{0}_supervisor div'.format(name));

    dropdown.onchange = function () {
        $.ajax({
            url: url,
            data: {
                'pk': this.value,
            },
            success: function (data) {
                supervisor.innerText = data;
            }
        });
    };
}

bind_selector("first");
bind_selector("second");


