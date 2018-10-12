import marked from 'marked';
import hljs from 'highlight.js';

// see: https://marked.js.org/#/USING_ADVANCED.md#options
marked.setOptions({
    highlight: function(code) {
        return hljs.highlightAuto(code).value;
    }
});

const markedWithHljs = (value) => (
    marked(value)
);

export {markedWithHljs}; 