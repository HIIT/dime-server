var res;

function parseResponse(data) {
    var text = "<table class=\"table\">";
    for (var i=0; i<data.length; i++) {
	var perc = data[i]["percentage"].toFixed(2);
	var n = data[i]["nevents"];

	text += "<tr><td>" + data[i]["actor"] + " (" + n + ") </td>";

	text += "<td width=\"60%\"><div class=\"progress\">\n" +
	    "<div class=\"progress-bar\" role=\"progressbar\" aria-valuenow=\"" + perc +
	    "\" aria-valuemin=\"0\" aria-valuemax=\"100\" style=\"width: " + perc + "%;\">\n" +  perc + 
	    "</div>\n</div>\n";
	
	text += "</td></tr>";
    }
    text += "</table>";
    document.getElementById("content").innerHTML = text;
}

