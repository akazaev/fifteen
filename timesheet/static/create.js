$(document).ready(function () {
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
                console.log(colors[obj.val()]);
                obj.css("background-color", colors[obj.val()]);
                obj.closest('tr').css("background-color", colors[obj.val()]);
            }
        });
    });
});
