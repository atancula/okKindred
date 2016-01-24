$(document).ready(function(){

    load_comments();

    $('#comment_submit').click(post_comment);

    $('#comment_input_text').keyup(function(e) {
        // If enter pressed
        if (e.keyCode == 13) {
            if (e.shiftKey || e.ctrlKey || e.altKey) {
                // new line
                $('#comment_input_text').value = $('#comment_input_text').value + "\n";
            }
            else {
                post_comment();
            }
            return false;
        }
    });

});

function post_comment() {

    if($('#comment_input_text').val()==null || $('#comment_input_text').val()=="") {
        return;
    }

    // show loading animation
    $('#comments_loading').show();

    // serialize form data
    var serializedFormData = $("#comment_form").serialize();



    // Fire off the request
    request = $.ajax({
        url: "/comment/post/",
        dataType: "json",
        type: "post",
        data: serializedFormData,
        success: function (data) {
            append_new_comments(data);
            $("#comment_input_text").val('');
        }
    });
}

function load_comments() {
    var content_type = $("#comment_container").data("content_type");
    var object_id = $("#comment_container").data("object_id");

     $.ajax({
        type: "GET",
        dataType: "json",
        url: "/comment/get/",
        data: { "content_type" : content_type, "object_id" : object_id },
        success: function (data) {
            append_new_comments(data);
        }
    });

}

function append_new_comments(data) {
     $('#comments_loading').hide();

    var html = [];
    var template = $('#comment_template').html();

    for (var i in data){
        var data_row = data[i];

        if (data_row.thumb == '' || data_row.thumb == null){
            image_url = "/static/img/portrait_80.png";
        }
        else{
            image_url = "/media/" + data_row.thumb;
        }

        var comment = {
            id: data_row.id,
            person_id : data_row.person_id,
            person_name: data_row.person_name,
            image_url: image_url,
            comment: data_row.comment,
            when_posted: data_row.creation_date
        };

        var output = Mustache.render(template, comment);
        html.push(output);
    }

    $('#comments_container').append(html.join(''));
}


