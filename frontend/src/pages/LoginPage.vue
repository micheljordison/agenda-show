<template>
  <q-layout view="hHh lpR fFf">
    <q-page-container>
      <q-page class="login-page page-gradient">
        <section class="login-shell">
          <div class="login-brand">
            <span class="brand-mark">
              <q-icon name="event_available" />
            </span>
            <h1>Agenda</h1>
            <p>Compromissos, participantes e confirmacoes em um calendario limpo.</p>
          </div>

          <div class="login-panel stack-md app-panel">
            <div class="login-panel-heading">
              <h2>Entrar</h2>
              <span>Use seu usuario e senha.</span>
            </div>
            <LoginForm :loading="auth.loading" :error="auth.error" @submit="handleLogin" />
          </div>
        </section>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { useRouter } from 'vue-router'
import LoginForm from '../components/LoginForm.vue'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()

async function handleLogin({ username, password }) {
  await auth.login(username, password)
  router.push('/')
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: clamp(1rem, 5vw, 3rem);
}

.login-shell {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(20rem, 28rem);
  gap: clamp(1.25rem, 5vw, 4rem);
  align-items: center;
  width: min(92vw, 68rem);
}

.login-brand {
  display: grid;
  gap: 1rem;
}

.brand-mark {
  display: inline-grid;
  width: 4rem;
  height: 4rem;
  place-items: center;
  border-radius: calc(var(--radius-app) + 0.25rem);
  background: rgb(var(--color-primary));
  color: white;
  font-size: 2rem;
  box-shadow: 0 1.2rem 2.5rem rgb(var(--color-primary) / 0.22);
}

.login-panel {
  width: 100%;
  padding: clamp(1.25rem, 4vw, 2.25rem);
  border-radius: calc(var(--radius-app) + 0.5rem);
}

h1,
h2,
p {
  margin: 0;
}

h1 {
  color: rgb(15 23 42);
  font-size: clamp(3rem, 8vw, 5.4rem);
  line-height: 0.95;
  font-weight: 850;
}

h2 {
  margin: 0 0 0.375rem;
  color: rgb(15 23 42);
  font-size: clamp(1.7rem, 4vw, 2.25rem);
  line-height: 1;
  font-weight: 800;
}

p {
  max-width: 32rem;
  color: rgb(100 116 139);
  font-size: clamp(1rem, 2vw, 1.15rem);
}

.login-panel-heading span {
  color: rgb(100 116 139);
}

@media (max-width: 48rem) {
  .login-shell {
    grid-template-columns: 1fr;
  }

  .login-brand {
    text-align: center;
    justify-items: center;
  }
}
</style>
