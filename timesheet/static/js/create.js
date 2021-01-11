$(document).ready(function () {
    $('.activity').each(function(){
        obj = $(this);
        color = colors[obj.val()];
        if (color) {
            obj.css("background-color", color);
            tr = obj.closest('tr')
            tr.find('.interval_block').css("background-color", color);
            tr.find('.activity_block').css("background-color", color);
        }
    });
    $('.activity').on('change', function(event){
        obj = $(this);
        $.ajax({
            type: "POST",
            headers: {
                'X-CSRFToken': csrf_token
            },
            url: "/timesheet/create/",
            data: {
                'time': obj.attr('time'),
                'activity': obj.val()
            },
            error: function () {
                obj.closest('tr').find('.status').text("⛔");
            },
            success: function (response) {
                if (response.status == 'ok') {
                    obj.closest('tr').find('.status').text("✔");
                };
                if (response.status == 'error') {
                    obj.closest('tr').find('.status').text("⛔");
                };
                color = colors[obj.val()];
                if (color) {
                    obj.css("background-color", color);
                    tr = obj.closest('tr')
                    tr.find('.interval_block').css("background-color", color);
                    tr.find('.activity_block').css("background-color", color);
                }
            }
        });
    });
});
