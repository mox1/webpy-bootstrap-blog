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
	//This will edit the social media links to set them to the correct urls
	var page = encodeURIComponent(window.location.href);
	var tw_href = 'http://twitter.com/home?status=Check+this+out+' + page;
	$('#tweet').attr('href',tw_href);
	var gp_href = 'https://plus.google.com/share?url=' + page;
	$('#gplus').attr('href',gp_href);
	var fb_href = 'http://www.facebook.com/sharer.php?u=' + page;
	$('#fb').attr('href',fb_href);
	
});
