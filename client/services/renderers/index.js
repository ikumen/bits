import marked from 'marked';
import hljs from 'highlight.js';

marked.setOptions({
    gfm: true,
    pedantic: false,
    sanitize: true,
    highlight: function(code) {
        return hljs.highlightAuto(code).value;
    }
});

const markedWithHljs = (value) => (
    marked(value)
);

export {markedWithHljs}; 