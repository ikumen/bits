<script>
  import micromark from "micromark";
  import gfmSyntax from "micromark-extension-gfm";
  import gfmHtml from "micromark-extension-gfm/html";
  import "./codemirror.css";

  export let content;

  $: rendered = micromark(content, {
    allowDangerousHtml: true,
    extensions: [gfmSyntax()],
    htmlExtensions: [gfmHtml]
  });
</script>

<div>
  {@html rendered}
</div>
