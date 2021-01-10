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
                'activity': obj.val()
            },
            success: function () {
                console.log('done');
            }
        });
    });
});
