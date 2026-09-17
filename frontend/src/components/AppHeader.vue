<template>
  <q-header class="app-header text-dark">
    <q-toolbar class="header-toolbar">
      <q-toolbar-title class="text-weight-bold">Compromissos</q-toolbar-title>
      <q-chip v-if="user?.is_master" color="primary" text-color="white">Master</q-chip>
      <q-btn flat round icon="logout" @click="$emit('logout')">
        <q-tooltip>Sair</q-tooltip>
      </q-btn>
    </q-toolbar>
  </q-header>
</template>

<script setup>
defineProps({
  user: Object
})

defineEmits(['logout'])
</script>

<style scoped>
.app-header {
  background: rgb(var(--color-surface) / 0.84);
  border-bottom: 0.0625rem solid rgb(148 163 184 / 0.32);
  backdrop-filter: blur(1rem);
}

.header-toolbar {
  width: min(94vw, 82rem);
  margin: 0 auto;
  padding-inline: 0;
}
</style>
