function fetch(event) {
    var num = $("#event_key").val();
    if (num === "" || isNaN(num)) {
        num = 2;
    }
    else if (event === "next") {
        num = parseInt(num) + 1;
        if (num < 2) {
            num = 2;
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
        data: { 'id': num, "opt": 0 },
        success: function (response) {
            $("#event_key").val(response["event_key"]);
            $("#event_title").val(response["event_title"]);
            $("#event_url").val(response["url"]);
            $("#event_text").val(response["event_text"]);
        }
    });
    return false;


}
function annot(e) {
    var genre = e.innerHTML;
    $.ajax({
        type: 'GET',
        url: '/annot',
        data: { 'id': $("#event_key").val(), 'genre': genre },
        success: function (response) {
            console.log(response);
            $("#next").trigger("click");
        }
    });
}
function logmeout() {
    console.log("Setting dat and time");
    var today = new Date().toISOString().slice(0, 10);
    var now = new Date().toLocaleString('en-GB').slice(12);
    $("#log_date").val(today);
    $("#log_time").val(now);
    return true;

}