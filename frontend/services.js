import marked from 'marked';
import hljs from 'highlight.js/lib/highlight';
import javascript from 'highlight.js/lib/languages/javascript';
import python from 'highlight.js/lib/languages/python';

hljs.registerLanguage('javascript', javascript);
hljs.registerLanguage('python', python);


const APP_JSON_MIMETYPE = 'application/json';
const APP_JSON_HEADERS = {
  'Content-Type': APP_JSON_MIMETYPE,
  'Accept': APP_JSON_MIMETYPE 
}

/** */
class FetchClient {
  constructor() {
    this.opts = {
      headers: APP_JSON_HEADERS,
    }
  }
  /**
   * Check if endpoint returned an error, in which we forward to error page.
   * @param {Response} resp
   */
  checkForErrors(resp) {
    const {status} = resp;
    if (status >= 400) {
      window.location.replace(`/errors/${status}`);
    }
    return resp;
  }

  /**
   * Wrapper for a fetch GET request.
   * @param {string} url 
   * @param {object} opts 
   */
  get(url, opts = {}) {
    return this._fetch(url, {method: 'GET', ...opts});
  }

  create(url, opts = {}) {
    return this._fetch(url, {method: 'POST', ...opts});
  }

  update(url, opts = {}) {
    return this._fetch(url, {method: 'PATCH', ...opts});
  }

  delete(url, opts = {}) {
    return this._fetch(url, {method: 'DELETE', ...opts});
  }

  async _fetch(url, opts = {}) {
    return await fetch(url, {
        method: 'GET',
        headers: APP_JSON_HEADERS, ...opts})
      .then(this.checkForErrors)
      .then(resp => {
        if (resp.status === 200 || resp.status === 201)
          return resp.json();
        return resp;
      })
      .catch(console.warn)
  }
}


class BitService {
  constructor() {
    this.fetchClient = new FetchClient();
  }

  create(bit) {
    return this.fetchClient.create('/api/bits', 
      {body: this._bitToJson(bit)});
  }

  update(bit) {
    return this.fetchClient.update(`/api/bits/${bit.id}`,
      {body: this._bitToJson(bit)});
  }

  _bitToJson(bit) {
    return JSON.stringify({
      description: bit.description,
      content: bit.content,
      published_at: bit.published_at
    });
  }

  get(id) {
    return this.fetchClient.get(`/api/bits/${id}`)
  }

  all() {
    return this.fetchClient.get('/api/bits');
  }

  delete(id) {
    return this.fetchClient.delete(`/api/bits/${id}`);
  }
}

class UserService {
  constructor() {
    this.fetchclient = new FetchClient()
  }

  stats() {
    return this.fetchclient.get('/api/user/stats');
  }

  reload() {
    return this.fetchclient.get('/sync/download')
  }

  getCurrentUser() {
    return this.fetchclient.get('/api/user');
  }
}

function getDateParts(isoDateString, locale='en-US') {
  const d = new Date(isoDateString);
  return {
    year: d.toLocaleString(locale, {year: 'numeric'}),
    monthDay: d.toLocaleString(locale, {month: 'long', day: 'numeric', timeZone: 'UTC'})
  }
}

/* 
* Configure marked with highlightjs
* see: https://marked.js.org/#/USING_ADVANCED.md#options 
*/
marked.setOptions({
  highlight: function(code) {
    return hljs.highlightAuto(code).value;
  }
})

const MarkedWithHljs = (value) => (
  marked(value)
)

module.exports = {
  BitService: new BitService(),
  UserService: new UserService(),
  MarkedWithHljs,
  getDateParts,
};
