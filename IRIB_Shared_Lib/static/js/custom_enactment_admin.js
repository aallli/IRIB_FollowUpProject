/**
 * Created by Ali.NET on 3/4/2021.
 */
if (!$) {
    $ = django.jQuery;
}

$(document).ready(function () {
    function set_enactment_help_text() {
        var div = document.querySelector('div.help');
        if(div)
            div.outerHTML = '<span class="help">لطفا نام و تاریخ ثبت را قبل از توضیحات درج فرمایید.</span>';
    }

    set_enactment_help_text();

    function bind_selector() {
        var dropdowns = document.querySelectorAll('[id^=id_followup_set-][id$=-actor]');
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
});