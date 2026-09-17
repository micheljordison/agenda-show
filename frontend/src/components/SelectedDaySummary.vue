<template>
  <section class="selected-day app-panel">
    <div class="selected-day-heading">
      <div>
        <p>Dia selecionado</p>
        <h2>{{ dateLabel }}</h2>
      </div>
      <q-btn color="primary" icon="add" label="Novo" unelevated @click="$emit('create')" />
    </div>

    <div v-if="appointments.length === 0" class="selected-day-empty">
      Nenhum compromisso para este dia.
    </div>

    <div v-else class="selected-day-items">
      <button
        v-for="appointment in appointments"
        :key="appointment.id"
        type="button"
        class="selected-day-item"
        @click="$emit('edit', appointment)"
      >
        <span>{{ timeLabel(appointment.start_datetime) }}</span>
        <strong>{{ appointment.title }}</strong>
      </button>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  date: {
    type: String,
    required: true
  },
  appointments: {
    type: Array,
    required: true
  }
})

defineEmits(['create', 'edit'])

const dateLabel = computed(() => {
  return new Date(`${props.date}T12:00:00`).toLocaleDateString('pt-BR', {
    weekday: 'long',
    day: '2-digit',
    month: 'long'
  })
})

function timeLabel(value) {
  return new Date(value).toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.selected-day {
  display: grid;
  gap: 1rem;
  padding: clamp(1rem, 2vw, 1.25rem);
}

.selected-day-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.selected-day-heading p,
.selected-day-heading h2 {
  margin: 0;
}

.selected-day-heading p {
  color: rgb(var(--color-primary));
  font-size: 0.75rem;
  font-weight: 800;
  text-transform: uppercase;
}

.selected-day-heading h2 {
  margin-top: 0.2rem;
  color: rgb(15 23 42);
  font-size: clamp(1.1rem, 3vw, 1.45rem);
  line-height: 1.15;
  text-transform: capitalize;
}

.selected-day-empty {
  border: 0.0625rem dashed rgb(var(--color-primary) / 0.26);
  border-radius: var(--radius-control);
  color: rgb(71 85 105);
  padding: 1rem;
}

.selected-day-items {
  display: grid;
  gap: 0.55rem;
}

.selected-day-item {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 0.75rem;
  align-items: center;
  width: 100%;
  border: 0;
  border-radius: var(--radius-control);
  background: rgb(var(--color-primary) / 0.08);
  color: rgb(15 23 42);
  cursor: pointer;
  padding: 0.75rem 0.85rem;
  text-align: left;
}

.selected-day-item span {
  color: rgb(var(--color-primary));
  font-weight: 800;
}

.selected-day-item strong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
