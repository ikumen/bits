'use strict';
var Bits = (function() {
	
	var isBits = function(files) {
		for(var file in files) {
			if(file.toLowerCase() === 'readme.md') {
				return true;
			}					
		}
		return false;
	}

	var respListener = function() {
		var gists = JSON.parse(this.responseText);
		var bitsContainer = document.getElementById('bits');
		gists.forEach(function(gist) {
			if(isBits(gist.files)) {
				var desc = document.createElement('h1');
				desc.appendChild(document.createTextNode(gist.description));

				bitsContainer.appendChild(desc);
				console.log(gist);
			}
		});
	}

	// var xhr = new XMLHttpRequest();
	// xhr.addEventListener('load', respListener);
	// xhr.open('GET', 'https://api.github.com/users/ikumen/gists');
	// xhr.send();

	// document.getElementById('content').innerHTML =
	// 	marked('#### heading 4');

	return {};

})();