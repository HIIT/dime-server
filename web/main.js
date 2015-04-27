var res;

function parseResponse(answer) {
    var text = "<table class=\"table\">";
    for (var j=0; j<answer.length; j++) {
	var date = new Date(answer[j]["date"]);
	var hist = answer[j]["hist"];

	text += "<thead><th><b>" + date.toDateString() + "</b></th><th></th></thead>\n";

	var l = hist.length;
	if (l > 5) 
	    l = 5;
	for (var i=0; i<l; i++) {
	    var perc = hist[i]["percentage"].toFixed(2);
	    var n = hist[i]["nevents"];
	    var name = hist[i]["actor"];
	    var url = null;

	    if (name == null)
		name = hist[i]["origin"];
	    if (name == null) {
		url = hist[i]["subject"]["uri"];
		if (url != null) {
		    name = url.replace(/^.*[\\\/]/, '');
		    if (name == "")
			name = url;
		}
	    }
	    if (name == null)
		name = "Unknown";

	    if (url == null) {
		text += "<tr><td>" + name.substring(0,40) + " (" + n + ") </td>";
	    } else {
		text += "<tr><td><a href=\"" + url + "\">" + 
		    name.substring(0,40) + "</a> (" + n + ") </td>";
	    }
	    
	    text += "<td width=\"60%\"><div class=\"progress\">\n" +
		"<div class=\"progress-bar\" role=\"progressbar\" aria-valuenow=\"" + perc +
		"\" aria-valuemin=\"0\" aria-valuemax=\"100\" style=\"width: " + perc 
		+ "%;\">\n" +  perc + 
		"</div>\n</div>\n";
	
	    text += "</td></tr>";
	}
    }
    text += "</table>";
    document.getElementById("content").innerHTML = text;
}

