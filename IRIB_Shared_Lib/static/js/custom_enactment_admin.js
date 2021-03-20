/**
 * Created by Ali.NET on 3/4/2021.
 */
if (!$) {
    $ = django.jQuery;
}

var counter = 0;
var max_try = 20;
function set_enactment_help_text() {
    var div = document.querySelector('div.help');
    if (!div) {
        if (counter > max_try) return;
        setTimeout(set_enactment_help_text, 1000);
        return;
    }
    div.outerHTML = '<span class="help">لطفا نام و تاریخ ثبت را قبل از توضیحات درج فرمایید.</span>';
}


set_enactment_help_text();
