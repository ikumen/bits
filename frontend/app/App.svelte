<script>
  import { Router, Route } from "svelte-routing";
  import User from "./pages/User.svelte";
  import Home from "./pages/Home.svelte";
  import Bit from "./pages/Bit.svelte";
</script>

<Router>
  <Route path="/@:user" component={User} />
  <Route path="/bits/:id" component={Bit} />
  <Route path="*" component={Home} />
</Router>

<!-- <script lang="ts">
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
    <div>{bit.user}</div>
  {/await}

	<Editor bind:editor {options} />	
  <Viewer {content} />
</main>



<style>
</style> -->
