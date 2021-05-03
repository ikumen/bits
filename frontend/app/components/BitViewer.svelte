<script>
  import micromark from "micromark";
  import gfmSyntax from "micromark-extension-gfm";
  import gfmHtml from "micromark-extension-gfm/html";
  import "./editor.css";

  export let bit;

  $: rendered = micromark(bit.content, {
    allowDangerousHtml: true,
    extensions: [gfmSyntax()],
    htmlExtensions: [gfmHtml]
  });
</script>

<style>
  .viewer {
    width: 100%;
  }
</style>

<div class="viewer">
  {@html rendered}
</div>
