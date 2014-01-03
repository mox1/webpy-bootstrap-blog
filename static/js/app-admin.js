//JS for the Admin page

//

$(document).ready(function(){
	//Load posts when user clicks button
	$('#manageposts').on('click',function(e) {
		$.ajax({
			dataType: "html",
			type: "POST",
			url: "",
			data: "method=getallposts" ,
			success: function(html) {
				$('#postdata').html(html);
				//$('#postdata').dataTable();
			},
			beforeSend: function() {
				$('#postdata').html("<p>Loading...</p>");
			}
		});
	});
	//Load image when user clicks button
	$('#manageimages').on('click',function(e) {
		$.ajax({
			dataType: "html",
			type: "POST",
			url: "",
			data: "method=getallimages" ,
			success: function(html) {
				$('#imagedata').html(html);
			},
			beforeSend: function() {
				$('#imagedata').html("<p>Loading...</p>");
			}
		});
	});
});