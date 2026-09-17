<template>
  <header class="calendar-topbar">
    <q-btn flat round icon="menu">
      <q-tooltip>Menu</q-tooltip>
      <q-menu class="topbar-menu">
        <q-list>
          <q-item clickable v-close-popup @click="$emit('update:viewMode', 'month')">
            <q-item-section avatar><q-icon name="calendar_month" /></q-item-section>
            <q-item-section>Mes</q-item-section>
          </q-item>
          <q-item clickable v-close-popup @click="$emit('update:viewMode', 'day')">
            <q-item-section avatar><q-icon name="calendar_today" /></q-item-section>
            <q-item-section>Dia</q-item-section>
          </q-item>
          <q-separator />
          <q-item clickable v-close-popup @click="$emit('logout')">
            <q-item-section avatar><q-icon name="logout" /></q-item-section>
            <q-item-section>Sair</q-item-section>
          </q-item>
        </q-list>
      </q-menu>
    </q-btn>

    <div class="topbar-title">
      <q-btn flat round dense icon="chevron_left" @click="$emit('previous')">
        <q-tooltip>Anterior</q-tooltip>
      </q-btn>
      <strong>{{ periodLabel }}</strong>
      <q-btn flat round dense icon="chevron_right" @click="$emit('next')">
        <q-tooltip>Proximo</q-tooltip>
      </q-btn>
    </div>

    <div class="topbar-actions">
      <q-btn flat round icon="search">
        <q-tooltip>Buscar</q-tooltip>
      </q-btn>
      <q-btn flat round icon="today" @click="$emit('today')">
        <q-tooltip>Hoje</q-tooltip>
      </q-btn>
      <q-btn flat round :icon="viewMode === 'month' ? 'calendar_view_month' : 'calendar_today'">
        <q-tooltip>Visualizacao</q-tooltip>
        <q-menu class="topbar-menu">
          <q-list>
            <q-item clickable v-close-popup :active="viewMode === 'month'" @click="$emit('update:viewMode', 'month')">
              <q-item-section avatar><q-icon name="calendar_view_month" /></q-item-section>
              <q-item-section>Mes</q-item-section>
            </q-item>
            <q-item clickable v-close-popup :active="viewMode === 'day'" @click="$emit('update:viewMode', 'day')">
              <q-item-section avatar><q-icon name="calendar_today" /></q-item-section>
              <q-item-section>Dia</q-item-section>
            </q-item>
          </q-list>
        </q-menu>
      </q-btn>
      <q-btn class="desktop-create" color="primary" round icon="add" unelevated @click="$emit('create')">
        <q-tooltip>Novo compromisso</q-tooltip>
      </q-btn>
    </div>
  </header>
</template>

<script setup>
defineProps({
  viewMode: {
    type: String,
    required: true
  },
  periodLabel: {
    type: String,
    required: true
  }
})

defineEmits(['update:viewMode', 'create', 'previous', 'next', 'today', 'logout'])
</script>

<style scoped>
.calendar-topbar {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: clamp(0.35rem, 1.5vw, 0.75rem);
  min-height: 4rem;
  padding-inline: clamp(0.35rem, 1.5vw, 0.8rem);
}

.topbar-title {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  min-width: 0;
}

.topbar-title strong {
  overflow: hidden;
  color: rgb(31 41 55);
  font-family: var(--font-display);
  font-size: clamp(1.45rem, 6vw, 2.25rem);
  font-weight: 650;
  line-height: 1;
  text-overflow: ellipsis;
  text-transform: capitalize;
  white-space: nowrap;
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 0.15rem;
}

.topbar-menu {
  border-radius: calc(var(--radius-app) - 0.25rem);
}

@media (max-width: 42rem) {
  .calendar-topbar {
    width: 100%;
  }

  .desktop-create {
    display: none;
  }

  .topbar-title {
    justify-content: center;
  }

  .topbar-title strong {
    max-width: 42vw;
  }
}
</style>
