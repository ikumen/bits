<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import CodeMirror from 'codemirror';
  import 'codemirror/mode/markdown/markdown';
  import './editor.css';

  const dispatch = createEventDispatcher();

  export let lineNumbers: Boolean = true;
  export let bit;

  let editor: CodeMirror;
  let editorEl;
  let options = {
    lineNumbers,
    lineWrapping: true,
    mode: 'markdown',
    value: bit.content
  };

  function createEditor(options) {
    if (!editor) {
      editor = CodeMirror(editorEl, options);
      editor.on('change', (cm, ch) => {
        dispatch('change', {
          cm, ch,
          content: cm.getValue()
        });
      })
    }
  }

  onMount(() => {
    createEditor(options);
  });
</script>

<div bind:this={editorEl} />
