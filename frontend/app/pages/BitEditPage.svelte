<script>
  import BitEditor from '../components/BitEditor.svelte';
  import BitViewer from '../components/BitViewer.svelte';
  import bitservice from '../services/bits';

  export let id; 
  
  let isPreview = true;
  let bit = {};

  async function loadBit(id) {
    bit = await bitservice.load(id);
  }

  function onChange(evt) {
    bit.content = evt.detail.content;
  }

  async function onSave(evt) {
    await bitservice.save(bit);
  }

</script>

<style>
  .biteditor {
    display: flex;
    width: 100%;
    align-items: stretch;
    align-content: stretch;
    background-color: gray;
    padding: 1px;
    height: 300px;
  }
  .biteditor .viewer {
    background-color: white;
    margin-left: 1px;
    padding: 0 10px;
    overflow-y: auto;
  }
  .biteditor .editor {
    /* background-color: white; */
  }

  :global(.full-width) {
    width: 100%;
  }

  :global(.split-width) {
    width: 50%;
  }
</style>

{#await loadBit(id)}
  ...loading bit
{:then} 
  <div class="biteditor">
    <div class="editor" 
        class:full-width={!isPreview}
        class:split-width={isPreview}>
      <BitEditor
        on:change={onChange}
        lineNumbers={false}
        bit={bit}
      />
    </div>
    {#if isPreview}
      <div class="viewer"
          class:split-width={isPreview}>
        <BitViewer
          bit={bit}
        />
      </div>
    {/if}
  </div>
  <div>
    <button on:click={() => isPreview = !isPreview}>{isPreview ? 'hide' : 'show'}</button>
    <button on:click={onSave}>save</button>
  </div>
{:catch}
  <h3>Doh, looks like we're having some issues please try again later</h3>
{/await}
