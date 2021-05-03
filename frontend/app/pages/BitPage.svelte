<script>
  import BitViewer from '../components/BitViewer.svelte';
  import bitservice from '../services/bits';

  export let id; 

</script>

<style>
  .sidebyside {
    display: flex;
    width: 100%;
    align-items: stretch;
    align-content: stretch;
    background-color: gray;
    padding: 1px;
  }
  .sidebyside :global(.viewer) {
    background-color: white;
    margin-left: 1px;
    padding: 0 10px;
    height: 300px;
  }
  .sidebyside :global(.editor) {
    padding-top: 10px;
    background-color: white;
  }

  .sidebyside :global(.editor), 
  .sidebyside :global(.viewer) {
    width: 100%;
  }
</style>

{#await bitservice.load(id)}
  ...loading bit
{:then bit} 
  <div class="sidebyside">
    <BitViewer class="viewer" 
      bit={bit}
    />
  </div>
{:catch}
  <h3>Doh, looks like we're having some issues please try again later</h3>
{/await}
