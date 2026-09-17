<template>
  <q-form class="login-form stack-sm" @submit.prevent="submit">
    <q-input v-model="username" label="Usuario" outlined autocomplete="username" lazy-rules :rules="[required]">
      <template #prepend>
        <q-icon name="person" />
      </template>
    </q-input>
    <q-input
      v-model="password"
      label="Senha"
      outlined
      type="password"
      autocomplete="current-password"
      lazy-rules
      :rules="[required]"
    >
      <template #prepend>
        <q-icon name="lock" />
      </template>
    </q-input>
    <ErrorState v-if="error" :message="error" />
    <q-btn class="full-width" label="Entrar" icon="login" color="primary" type="submit" :loading="loading" unelevated />
  </q-form>
</template>

<script setup>
import { ref } from 'vue'
import ErrorState from './state/ErrorState.vue'

defineProps({
  loading: Boolean,
  error: String
})

const emit = defineEmits(['submit'])
const username = ref('')
const password = ref('')

function required(value) {
  return Boolean(value) || 'Campo obrigatorio'
}

function submit() {
  emit('submit', { username: username.value, password: password.value })
}
</script>

<style scoped>
.login-form {
  width: 100%;
}
</style>
