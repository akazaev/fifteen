$(document).ready(function () {
    $('.activity').each(function(){
        obj = $(this);
        color = colors[obj.val()];
        if (color) {
            obj.css("background-color", color);
            obj.closest('tr').css("background-color", color);
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
            success: function () {
                obj.css("background-color", colors[obj.val()]);
                obj.closest('tr').css("background-color", colors[obj.val()]);
            }
        });
    });
});
