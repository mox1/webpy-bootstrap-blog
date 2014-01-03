//


//Set the hidden reply-to field when a user clicks on the reply-to field
//also set the title
$(document).ready(function(){
	$('.replyto').on('click',function(e) {
		r_to = $(this).attr('commentid');
		r_title = $('#ctitle'+r_to).html();
		$('#input-replyto').val(r_to);
		$('#input-comment-title').val('RE: ' + r_title);
	});
	//anti spam, set a hidden field when user clicks submit
	$('#sbmt-btn').on('click', function(e) {
		$('#input-email').val('n0m0r3sp4m@n0p3.0rg');	
	});
	
});

