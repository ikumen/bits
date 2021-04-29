<script lang="ts">
import { onMount } from "svelte";

	import Editor from "./editor.svelte";
  import Viewer from "./viewer.svelte";

  async function listBits() {
    return fetch(`/api/bits`)
      .then(resp => resp.json());
  }

  async function newBit() {
    return fetch(`/api/bits/new`)
      .then(resp => resp.json());
  }

  async function saveBit(doc) {
    return fetch('/api/bits', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(doc)
    })
  }

  let editor;
  let content = '';

  const options = {
    mode: "markdown",
    //lineNumbers: true,
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
  {#await newBit()}
    <div>... loading bits</div>
  {:then bit} 
    <div>{bit.id}</div>
  {/await}

	<Editor bind:editor {options} />	
  <Viewer {content} />
</main>

<style>
</style>
