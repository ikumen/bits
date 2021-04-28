<script>
  import { onMount } from 'svelte';
  import CodeMirror from 'codemirror';
  import "codemirror/mode/markdown/markdown";
  import "./codemirror.css";
import { on } from 'codemirror';


  let classes = '';
  let editorEl;

  export let editor;
  export let options = {};
  //export { classes as class };

  function createEditor(options) {
    if (!editor){
      editor = CodeMirror(editorEl, options);
      editor.on('change', (cm, ch) => {
        console.log(editor.getValue())
      })
    }
  }

  $: if (editorEl) {
    createEditor(options);
  }

  onMount(() => {
    createEditor(options);
  })
</script>

<style>
  
</style>

<div bind:this={editorEl} />
