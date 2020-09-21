function fetch(event) {
    var num = $("#event_key").val();
    if (num === "" || isNaN(num)) {
        num = 2;
    }
    else if (event.srcElement.id === "next") {
        num = parseInt(num) + 1;
        if (num > 500) {
            num = 500;
        }
    }
    else {
        num = parseInt(num) - 1;
        if (num < 2) {
            num = 2;
        }
    }

    $.ajax({
        type: 'GET',
        url: '/fetch_data',
        data: { 'id': num },
        success: function (response) {
            $("#event_key").val(response["event_key"]);
            $("#event_title").val(response["event_title"]);
            $("#event_url").val(response["url"]);
            $("#event_text").val(response["event_text"]);
        }
    });
    return false;


}