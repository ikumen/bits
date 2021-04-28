<script lang="ts">
import { onMount } from "svelte";

	import Editor from "./editor.svelte";
  import Viewer from "./viewer.svelte";

  let editor;
  let content = '';

  const options = {
    mode: "markdown",
    lineNumbers: true,
    value: content
  }

  onMount(() => {
    if (editor) {
      editor.on("change", () => {
        content = editor.getValue();
      })
    }
  })

</script>

<main>
	<Editor bind:editor {options} />	
  <Viewer {content} />
</main>

<style>
</style>
