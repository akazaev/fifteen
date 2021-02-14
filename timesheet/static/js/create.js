function updateColors() {
    $('.activity').each(function(){
        obj = $(this);
        color = COLORS[obj.val()];

        if (color && color != '#FFFFFF') {
            obj.css("background-color", color);
            tr = obj.closest('tr')
            tr.find('.interval_block').css("background-color", color);
            tr.find('.activity_block').css("background-color", color);
        } else {
            obj.removeClass (function (index, className) {
                return (className.match (/(^|\s)rating\S+/g) || []).join(' ');
            });
            rating = RATINGS[obj.val()];
            obj.addClass("rating" + rating);
            tr = obj.closest('tr')
            tr.find('.interval_block').removeClass (function (index, className) {
                return (className.match (/(^|\s)rating\S+/g) || []).join(' ');
            });
            tr.find('.activity_block').removeClass (function (index, className) {
                return (className.match (/(^|\s)rating\S+/g) || []).join(' ');
            });
            tr.find('.interval_block').addClass("rating" + rating);
            tr.find('.activity_block').addClass("rating" + rating);
        }
    });
}

$(document).ready(function () {
    updateColors();

    $('.activity').on('change', function(event){
        obj = $(this);
        $.ajax({
            type: "POST",
            headers: {
                'X-CSRFToken': csrf_token
            },
            url: "/timesheet/create/",
            data: {
                'date': CUR_DATE,
                'time': obj.attr('time'),
                'activity': obj.val()
            },
            error: function () {
                obj.closest('div').find('.status').text("⛔");
            },
            success: function (response) {
                if (response.status == 'ok') {
                    obj.closest('div').find('.status').text("✔");
                };
                if (response.status == 'error') {
                    obj.closest('div').find('.status').text("⛔");
                };
                updateColors();
            }
        });
    });
});
