<script>
  import { Router, Route } from "svelte-routing";
  import UserPage from "./pages/UserPage.svelte";
  import HomePage from "./pages/HomePage.svelte";
  import BitPage from "./pages/BitPage.svelte";
  import BitEditPage from "./pages/BitEditPage.svelte";
</script>

<Router>
  <Route path="/@:user" component={UserPage} />
  <Route path="/bits/new">
    <BitEditPage id="new" />
  </Route>
  <Route path="/bits/:id/edit" let:params>
    <BitEditPage id={params.id} />
  </Route>
  <Route path="/bits/:id" let:params>
    <BitPage id={params.id} />
  </Route>
  <Route path="*" component={HomePage} />
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
