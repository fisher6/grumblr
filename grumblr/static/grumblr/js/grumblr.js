$('form#message').on('submit', function(event) {
  event.preventDefault(); // Prevent form from being submitted
	var form_data = $(this).serialize();
  // clear the textarea input box after user submitted his post
  $('#id_text').val('')
  $.ajax('/add-post', { // using ajax post to send the form data and change post button
    type: "POST",
    data: form_data,
		timeout: 3000, // 3000ms timeout
		beforeSend: function() { // function that runs when AJAX fetching starts
			$('button:contains("Post!")').removeClass('btn-success').addClass('btn-danger').text("Posting...");
		},
  });
});


$(function () {
  $('div').on('mouseenter', '.message-thread', function() {
    $(this).closest('div').find('button').show()
  });

  $('div').on('mouseleave', '.message-thread', function() {
    if (! $(this).find('textarea').is(':focus')) {
      $(this).closest('div').find('button').hide()
    }
  });

  $('body').on('submit', 'form.comment-form', function(event) {
    event.preventDefault(); // Prevent form from being submitted
  	var form_data = $(this).serialize();
    //console.log(form_data);
    // clear the textarea input box after user submitted his post
    $(this).closest('div').find('textarea').val('')
    /* instead of using:
    $.post("/add-post", form_data)
      .done(function(data) {
        updateChanges(data)
      });
    I can use $.ajax (which $.post is actually a syntactic sugar to $.ajax with type: 'POST') */
    $.ajax('/add-comment', { // using ajax post to send the form data and change post button
      type: "POST",
      data: form_data,
  		complete: function(response) {
        var response_json = JSON.parse(response.responseText);
        $('div#' + response_json.message_id).find('span textarea').before(
        '<div class="list-group-item disabled">' +
          '<div class="col-lg-2 post-pic">' +
            '<img src="' + response_json.profile_pic_url + '" class="img-responsive">' +
          '</div>' +
          '<div class="col-lg-2 post-name-date">' +
            '<a href="/profile/'+ response_json.user + '" class="post-name">' + response_json.user + '</a>' +
            '<br>' +
            '<span class="post-date">' + response_json.date + '</span>' +
          '</div>' +
          '<br>' +
          response_json.text +
          '<br><br>' +
        '</div>'
  		)},
  		timeout: 3000, // 3000ms timeout
    });
  });
});
// The following function will help you update the contents of the
// page based on our application's JSON response.
function updateChanges(data) {
  // Clear old errors
  main_error_div = $('.mainerror');
  main_error_div.empty();
  // Display new errors
  for(var i = 0; i < data.errors.length; i++) {
    //console.log(data.errors[i]);
    main_error_div.append('<li>' + data.errors[i] + '</li>');
  }

  // Process new messages
  for(var i = data.messages.length-1; i >= 0; i--) {
    $('#messages').prepend(
    '<form class="comment-form" action="comment" method="post">' +
      '<div id="' + data.messages[i]['id'] + '" class="list-group message-thread">' +
        '<div class="col-lg-2 post-pic">' +
          '<img src="' + data.messages[i]['profile_pic_url'] + '" class="img-responsive">' +
        '</div>' +
        '<div class="col-lg-2 post-name-date">' +
          '<a href="/profile/'+ data.messages[i]['user'] + '" class="post-name">' + data.messages[i]['user'] + '</a>' +
          '<br>' +
          '<span class="post-date">' + data.messages[i]['date'] + '</span>' +
        '</div>' +
        '<br>' +
        data.messages[i]['text'] +
        '<br><br>' +
    '<span>' +
      '<textarea cols="20" class="' + data.messages[i]['id'] + '" maxlength="42" name="text" placeholder="Reply" rows="1" required></textarea>' +
    '</span>' +
    '<button type="submit" class="btn btn-sm btn-success comment-btn">Comment</button>' +
    '<input type="hidden" class="message_id" value="' + data.messages[i]['id'] +'" name="message_id">' +
    '</div>' +
  '</form>' +
  '</div>'
    );
  }
  // Change Posting button back to post-date
  $('button:contains("Posting...")').removeClass('btn-danger').addClass('btn-success').text("Post!");
  // Update timestamp
  $('#timestamp').val(data.timestamp+10);
}


// The boilerplate code below is copied from the Django 1.10 documentation.
// It establishes the necessary HTTP header fields and cookies to use
// Django CSRF protection with jQuery Ajax requests.

$( document ).ready(function() {  // Runs when the document is ready

  // using jQuery
  // https://docs.djangoproject.com/en/1.10/ref/csrf/
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  }

  var csrftoken = getCookie('csrftoken');

  function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  }

  $.ajaxSetup({
      beforeSend: function(xhr, settings) {
          if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
              xhr.setRequestHeader("X-CSRFToken", csrftoken);
          }
      }
  });
  /* If we have .showmessages class,
  The global stream page should be updated with any new posts
  every five seconds, without refreshing the HTML page. */
  // sending AJAX get reqeust with current timestamp to get only messages posted after
  if ($("li").hasClass('showmessages')) {
    window.setInterval(function() {
      $.get("/get-new-messages", {
          'timestamp': $('#timestamp').attr('value'),
          'stream_type': $('li.active.showmessages').text(),
          'username_profile': $('a.username').text(),
        })
        .done(function(data) {
          updateChanges(data);
        });
    }, 500);
  }

}); // End of $(document).ready
