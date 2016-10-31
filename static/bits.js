var bits = (function() {
	'use strict';

	var post = (function() {
		/**
		 * Parses given string s representing a yaml document and loads 
		 * it into an object of key/value pairs. Specifically we're 
		 * looking for the following keys: title, date, tags, category,
		 * layout, published.
		 *
		 * @param {String} s string representing a yaml document
		 * @returns {Object} containing key and values
		 */
		var loadYaml = function(s) {
			var lines = s.trim().split(/\n/);
			var meta = {}, 
					key, 		// current key
					value,	// current value
					added = false;

			function addKeyValue(m, k, v) {
				if(k && v) {
					added = true;
					if(k === 'tags') {
						m[k] = m[k] || [];
						matches = v.match(/\[([\s\S]*)\]/);
						if(matches && matches.length >= 2 && matches[1].trim()) {
							matches[1].split(/,/).forEach(function(tag) {
								m[k].push(tag);
							});
						}
					} else {
						m[k] = v;
					}
				}
			}

			for(var i=0; i < lines.length; i++) {
				var matches = lines[i].match(/^\s*(title|date|created_at|tags|category|layout|published):([\s\S]*)$/);
				if(matches && matches.length >= 2 && matches[1] !== key) {					
					key = matches[1];
					value = (matches[2] || '').trim();
					addKeyValue(meta, key, value);
				}
			}
			return meta;
		}

		/**
		 * Parses a Jekyll style (ie, contains yaml front matter) into 
		 * meta data and content. 
		 *
		 * @param {String} s string representing a Jekyll style post
		 * @returns {Object} containing meta data and content from the 
		 * original post source
		 */
		var loadSource = function(s) {
			var post;
			var matches = s.match(/^\s*---([\s\S]*?)---([\s\S]*)$/);
			if(matches && matches.length >= 2) {
				var meta = loadYaml(matches[1])
				post = {title: meta.title, meta: meta, markdown: matches[2], source: s};
			}
			return post;
		};

		return {
			load: loadSource
		}

	})();

	function noOp() {}

	/**
	 * Very basic wrapper for common XHR tasks. 
	 * !!! TODO: there's no error handling !!!
	 */
	var xhr = (function() {
		var xhr = function(p) {
			this.opts = {
				headers: [],
				handlers: {ok: noOp, err: noOp},
				path: p
			}
		};
		xhr.prototype.ok = function(fn) {
			this.opts.handlers.ok = (fn || noOp); return this;
		};
		xhr.prototype.err = function(fn) {
			this.opts.handlers.err = (fn || noOp); return this;
		}
		xhr.prototype.header = function(k, v) {
			this.opts.headers.push({'k': k, 'v': v}); return this;
		}
		function doXhr(opts) {
			var _xhr = new XMLHttpRequest();
			_xhr.addEventListener('loadend', function() {
				if(this.status >= 400) {
					opts.handlers.err(this.status, this.statusText);
				} else {
					if(this.getResponseHeader('content-type') === 'application/json') {
						opts.handlers.ok(JSON.parse(this.responseText));
					} else {
						opts.handlers.ok(this.responseText);
					}
				}
			});
			_xhr.open(opts.method, opts.path);
			if(opts.method === 'GET') {
				_xhr.send();
			} else {
				opts.headers.forEach(function(hdr) {
					_xhr.setRequestHeader(hdr.k, hdr.v);
				});
				_xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
				_xhr.send(JSON.stringify(opts.data)); 
			}
		}
		xhr.prototype.get = function() {
			this.opts.method = 'GET';
			doXhr(this.opts);
		};
		xhr.prototype.send = function(data, m) {
			this.opts.method = (m||'POST').toUpperCase();
			this.opts.data = (data||'');
			doXhr(this.opts);
		}
		return function(p) {
			return new xhr(p);
		}
	})();

	/**
	 * Helper for working with DOM elements.
	 */
	var el = (function() {
		var _el = function(id) { this.elem = document.getElementById(id); }
		_el.prototype.text = function(t) { 
			this.elem.innerText = t; return this;	
		}
		_el.prototype.val = function(t) { 
			this.elem.value = t; return this; 	
		}
		_el.prototype.html = function(h) { 
			this.elem.innerHTML = h; return this;
		}
		_el.prototype.on = function(t, fn) {
			var elem = this.elem;
			this.elem.addEventListener(t, function(e) {
				fn(e);
			});
			return this;
		}
		_el.prototype.attr = function(n, v) {
			if(!v) {
				return this.elem.getAttribute(n);
			} else {
				this.elem.setAttribute(n, v);
				return this;
			}
		}
		_el.prototype.appendAll = function(arr, format, pos) {
			if(arr && arr instanceof Array && arr.length > 0) {
				pos = pos || 'beforeend';
				var elem = this.elem;

				arr.forEach(function(a) { 
					elem.insertAdjacentHTML(pos, format(a)); 
				});
			}
			return this;
		}
		_el.prototype.append = function(pos, h) {
			if(!h) {
				h = pos;
				pos = 'beforeend';
			}
			this.elem.insertAdjacentHTML(pos, h); 
			return this;
		}
		var createEl = function(id) {
			return new _el(id);
		}
		_el.prototype.el = createEl;
		return createEl;
	})();

	return {
		el: el,
		post: post,
		xhr: xhr
	}

})();


