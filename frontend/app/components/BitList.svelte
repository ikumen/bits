<script>

  async function getBits() {
    return fetch(`/api/bits`)
      .then(resp => resp.json());
  }

  let bits = getBits();

</script>

<ul>
  {#await bits}
    ...loading bits
  {:then bit} 
    {bit}
  {/await}
</ul>
