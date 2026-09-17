<template>
  <q-banner rounded class="bg-red-1 text-red-10">
    {{ message }}
  </q-banner>
</template>

<script setup>
defineProps({
  message: {
    type: String,
    required: true
  }
})
</script>
