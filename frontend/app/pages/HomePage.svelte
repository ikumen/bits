<script>
  import { Link } from "svelte-routing";
  import BitList from "../components/BitList.svelte";
</script>

<div>
  <div><Link to={"/bits/new"}>create new</Link></div>
  <BitList />
</div>
