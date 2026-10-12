
<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
import base from '../components/BaseLayout.vue'
export default{
  name: 'App',
  component:{
    base
  }
}

</script>

