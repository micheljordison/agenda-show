<template>
  <q-dialog
    :model-value="modelValue"
    transition-show="scale"
    transition-hide="scale"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <q-card class="appointment-modal app-panel">
      <q-card-section class="modal-heading">
        <div>
          <p class="modal-eyebrow">{{ appointment?.id ? 'Edicao' : 'Novo registro' }}</p>
          <h2>{{ appointment?.id ? 'Editar compromisso' : 'Novo compromisso' }}</h2>
          <span>Organize data, horario, descricao e local em um unico fluxo.</span>
        </div>
        <q-btn flat round icon="close" v-close-popup>
          <q-tooltip>Fechar</q-tooltip>
        </q-btn>
      </q-card-section>

      <q-card-section class="modal-form">
        <q-input v-model="form.title" label="Titulo" outlined autofocus />
        <q-input v-model="form.body" label="Descricao" outlined type="textarea" autogrow />
        <div class="modal-grid">
          <q-input v-model="form.start_datetime" label="Inicio" outlined type="datetime-local" />
          <q-input v-model="form.end_datetime" label="Fim" outlined type="datetime-local" />
        </div>
        <LocationMapPicker
          v-model="form.url_maps"
          v-model:location-name="form.location_name"
          v-model:latitude="form.location_lat"
          v-model:longitude="form.location_lng"
        />
      </q-card-section>

        <q-card-actions class="modal-actions">
          <q-btn
            v-if="appointment?.id"
            flat
            color="negative"
            icon="delete"
            label="Excluir"
            @click="$emit('delete', appointment)"
          />
          <q-btn v-else flat label="Cancelar" v-close-popup />

          <q-btn
            color="primary"
            icon="event_available"
            label="Salvar"
            unelevated
            @click="save"
          />
        </q-card-actions>
      
    </q-card>
  </q-dialog>
</template>

<script setup>
import { reactive, watch } from 'vue'
import LocationMapPicker from './LocationMapPicker.vue'

const props = defineProps({
  modelValue: Boolean,
  appointment: Object
})

const emit = defineEmits(['update:modelValue', 'save', 'delete'])

const form = reactive({
  title: '',
  body: '',
  start_datetime: '',
  end_datetime: '',
  url_maps: '',
  location_name: '',
  location_lat: null,
  location_lng: null
})

watch(
  () => [props.appointment, props.modelValue],
  () => {
    if (!props.modelValue) {
      return
    }

    form.title = props.appointment?.title || ''
    form.body = props.appointment?.body || ''
    form.start_datetime = props.appointment?.start_datetime?.slice(0, 16) || ''
    form.end_datetime = props.appointment?.end_datetime?.slice(0, 16) || ''
    form.url_maps = props.appointment?.url_maps || ''
    form.location_name = props.appointment?.location_name || ''
    form.location_lat = props.appointment?.location_lat ?? null
    form.location_lng = props.appointment?.location_lng ?? null
  },
  { immediate: true }
)

function save() {
  emit('save', { ...form })
}
</script>

<style scoped>
.appointment-modal {
  width: min(94vw, 42rem);
  overflow: hidden;
  border-radius: calc(var(--radius-app) + 0.5rem);
  background:
    linear-gradient(135deg, rgb(var(--color-primary) / 0.08), transparent 34%),
    rgb(var(--color-surface));
}

.modal-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: clamp(1rem, 3vw, 1.5rem);
}

.modal-heading h2 {
  margin: 0;
  color: rgb(15 23 42);
  font-size: clamp(1.45rem, 4vw, 2rem);
  line-height: 1.1;
}

.modal-heading span,
.modal-eyebrow {
  color: rgb(71 85 105);
}

.modal-eyebrow {
  margin: 0 0 0.35rem;
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0;
  text-transform: uppercase;
}

.modal-form {
  display: grid;
  gap: 0.9rem;
  padding: 0 clamp(1rem, 3vw, 1.5rem) clamp(1rem, 3vw, 1.5rem);
}

.modal-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.9rem;
}

.modal-actions {
  display: flex;
  justify-content: space-between;
  gap: 0.6rem;
  padding: clamp(1rem, 3vw, 1.25rem) clamp(1rem, 3vw, 1.5rem);
  background: rgb(248 250 252 / 0.88);
}

@media (max-width: 42rem) {
  .modal-grid {
    grid-template-columns: 1fr;
  }

  .modal-actions {
    align-items: stretch;
    flex-direction: column-reverse;
  }
}
</style>
