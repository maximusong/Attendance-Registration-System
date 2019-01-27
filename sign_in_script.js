$(function() {

var CLIENT_ID = '870182307965-ot2hu6a9gibq84l6ppkbuju2hu6paouh.apps.googleusercontent.com';
var DISCOVERY_DOCS = ["https://sheets.googleapis.com/$discovery/rest?version=v4"];
var SCOPES = "https://www.googleapis.com/auth/spreadsheets";

function initClient() {
  gapi.client.init({
    discoveryDocs: DISCOVERY_DOCS,
    clientId: CLIENT_ID,
    scope: SCOPES
  })
  .then( () => {
  	gapi.auth2.getAuthInstance().signIn();
  	console.log('binding')
  	$('#update-data').on('click', function() {
	  	getRow().then(rownum => updateData(rownum)).then(function(){
	  		$('#special-div').html('<h1>Late Sign-In details have been submitted. Thank you.</h1>');
	  	}).then(function(){
	  		var done_button = $('<button id="buttondone" type="button" class="btn btn-primary btn-lg"><a id="d" href="index.html">Done</a></button>');
	  		$('#special-div').append(done_button);
	  	})
	  	});
	}) 

}

function appendPre(message) {
	var pre = document.getElementById('content');
	var textContent = document.createTextNode(message + '\n');
	pre.appendChild(textContent);
}

function getRow() {
	return gapi.client.sheets.spreadsheets.values.get({
	  spreadsheetId: '1Bx59e7rxjh7joMw_yOR3T6McNlFGdjvCs0yLQBx5oCY',
	  range: 'A2:C',
	})
	.then(function(response) {
	  var range = response.result;
	  if (range.values.length > 0) {
	    appendPre('Student ID, Arrival Time, Date:');
	    var data = range.values;
	    var num = data.length

	    var row = data[num-1]
	    appendPre(row[0] + ', ' + row[1]+', '+row[2]);
	    document.getElementById("studentid").value=row[0];
        document.getElementById("time").value=row[1];
        document.getElementById("date").value=row[2];
	    return 1 + num
	  }
	})
}

function updateData(rownum) {
	let updateArg = {
		spreadsheetId: '1Bx59e7rxjh7joMw_yOR3T6McNlFGdjvCs0yLQBx5oCY',
		range: 'A'+ rownum+ ':G' + rownum,
		valueInputOption: 'USER_ENTERED',
		resource: {
			values: [ 
				[
			  		String(document.getElementById("studentid").value), 
			  		String(document.getElementById("time").value), 
			  		String(document.getElementById("date").value), 
			  		String(document.getElementById("lastname").value),
			  		String(document.getElementById("firstname").value),
			  		String(document.getElementById("tg").value),
			  		String(document.getElementById("reason").value), 
			  	]
			]
		}
	};


	gapi.client.sheets.spreadsheets.values.update(updateArg)
	.then(response => "update successful!!")
	.catch(err => console.log(err))

}


gapi.load('client:auth2', initClient);

setTimeout( () => {
	if (gapi.auth2.getAuthInstance().isSignedIn.get()) {

		// THIS IS WHERE YOU LOGIC STARTS

		console.log('Ready Now')
		getRow().then(row => console.log(row))

		//

	};
}, 1000)


})