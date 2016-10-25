var bits = (function() {
	'use strict';

	var _getmeta = function(data) {
		var lines = data.trim().split(/\n/)
		var meta = {}
		var key = '';			// current key
		var value = '';		// current value

		function addKeyValue(m, k, v) {
			if(k && v) {
				if(k === 'tags') {
					v = v.match(/\[([\s\S]*)\]/)[1].split(/,/)
				}
				m[k] = v;
			}
		}

		for(var i=0; i < lines.length; i++) {
			var matches = lines[i].match(/^\s*(title|created_at|tags):([\s\S]*)$/);
			if(matches && matches[1] !== key) {
				addKeyValue(meta, key, value);
				key = matches[1];
				value = matches[2].trim();
			}
		}
		addKeyValue(meta, key, value);
		return meta;
	}


	var _parse = function(s) {
		var matches = s.match(/^\s*---([\s\S]*?)---([\s\S]*)$/);
		var post = {meta: _getmeta(matches[1]), content: matches[2], raw: s};
		return post;
	};

	var fetch = function(p, cb) {
		var xhr = new XMLHttpRequest();
		xhr.addEventListener('load', function() {
			// send back parsed response
			cb(_parse(this.responseText));
		});
		xhr.open('GET', p);
		xhr.send();
	}

	var el = (function() {
		var _el = function(id) { this.elmt = document.getElementById(id); }
		_el.prototype.text = function(t) { this.elmt.innerText = t; return this; }
		_el.prototype.val = function(t) { this.elmt.value = t; return this; }
		_el.prototype.html = function(h) { this.elmt.innerHTML = h; return this; }
		_el.prototype.append = function(pos, h) {
			if(!h) {
				h = pos;
				pos = 'beforeend';
			}
			this.elmt.insertAdjacentHTML(pos, h); return this;
		}
		var createEl = function(id) {
			return new _el(id);
		}
		_el.prototype.el = createEl;
		return createEl;
	})();

	return {
		el: el,
		fetch: fetch,
		yaml: _getmeta
	}

})();

