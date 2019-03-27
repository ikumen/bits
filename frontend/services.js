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

function handleAsyncResponse(resp) {
    const { status } = resp;
    if (status === 200)
      return resp.json();
    if (status === 204)
      return resp;
    //for now everything else is an error  
    window.location.replace(`/errors/${status}`)
}

class BitService {

  async reload() {
    return await fetch('/api/settings/reload')
      .then(handleAsyncResponse)
  }

  async settings() {
    return await fetch('/api/settings')
      .then(handleAsyncResponse)
  }

  async save(bit) {
    const method = bit.id === 'new' ? 'POST' : 'PATCH';
    return await fetch(`/api/bits/${bit.id}`, {
          method: method,
          headers: APP_JSON_HEADERS,
          body: JSON.stringify({
            description: bit.description,
            content: bit.content
          })
        })
      .then(handleAsyncResponse)
  }

  async get(id) {
    return await fetch(`/api/bits/${id}`)
      .then(handleAsyncResponse)
}

  async all() {
    return await fetch('/api/bits')
      .then(handleAsyncResponse);
  }

  async delete(id) {
    return await fetch(`/api/bits/${id}`, {
      method: 'DELETE',
      headers: APP_JSON_HEADERS
    })
    .then(handleAsyncResponse)
  }
}

class UserService {
  async getCurrentUser() {
    return await fetch('/api/user')
      .then(handleAsyncResponse);
  }
}

function getDateParts(isoDateString, locale='en-US') {
  const d = new Date(isoDateString);
  return {
    year: d.toLocaleString(locale, {year: 'numeric'}),
    monthDay: d.toLocaleString(locale, {month: 'long', day: 'numeric'})
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
