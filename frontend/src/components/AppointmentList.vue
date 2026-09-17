<template>
  <q-list bordered separator class="appointment-list app-panel">
    <q-item v-for="appointment in appointments" :key="appointment.id" class="appointment-item">
      <q-item-section>
        <q-item-label class="text-weight-medium">{{ appointment.title }}</q-item-label>
        <q-item-label caption>{{ formatRange(appointment) }}</q-item-label>
        <q-item-label caption>{{ appointment.body }}</q-item-label>
      </q-item-section>
      <q-item-section side>
        <div class="actions">
          <q-btn flat round icon="check_circle" color="positive" @click="$emit('confirm', appointment)">
            <q-tooltip>Confirmar presenca</q-tooltip>
          </q-btn>
          <q-btn flat round icon="edit" @click="$emit('edit', appointment)">
            <q-tooltip>Editar</q-tooltip>
          </q-btn>
          <q-btn flat round icon="link_off" @click="$emit('unlink', appointment)">
            <q-tooltip>Desvincular</q-tooltip>
          </q-btn>
          <q-btn flat round icon="delete" color="negative" @click="$emit('remove', appointment)">
            <q-tooltip>Remover</q-tooltip>
          </q-btn>
        </div>
      </q-item-section>
    </q-item>
  </q-list>
</template>

<script setup>
defineProps({
  appointments: {
    type: Array,
    required: true
  }
})

defineEmits(['confirm', 'edit', 'unlink', 'remove'])

function formatRange(appointment) {
  const start = new Date(appointment.start_datetime).toLocaleString('pt-BR')
  const end = new Date(appointment.end_datetime).toLocaleString('pt-BR')
  return `${start} ate ${end}`
}
</script>

<style scoped>
.actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.25rem;
}

.appointment-list {
  overflow: hidden;
  border-color: rgb(148 163 184 / 0.35);
}

.appointment-item {
  padding-block: 0.75rem;
}

@media (max-width: 42rem) {
  .appointment-item {
    align-items: flex-start;
  }

  .actions {
    max-width: 6rem;
  }
}
</style>
