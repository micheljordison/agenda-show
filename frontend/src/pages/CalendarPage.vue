<template>
  <q-layout view="hHh lpR fFf">
    <q-page-container>
      <q-page class="calendar-page page-gradient">
        <div class="calendar-shell-page">
          <CalendarToolbar
            v-model:view-mode="viewMode"
            :period-label="periodLabel"
            @create="openCreate"
            @previous="movePeriod(-1)"
            @next="movePeriod(1)"
            @today="goToday"
            @logout="logout"
          />
          <LoadingState v-if="appointments.loading" />
          <ErrorState v-else-if="appointments.error" :message="appointments.error" />
          <template v-else>
            <AppointmentCalendar
              v-model="selectedDate"
              :appointments="appointments.items"
              :view-mode="viewMode"
              @create-date="openCreateAt"
              @edit="openEdit"
            />
          </template>

          <q-page-sticky position="bottom-right" :offset="[24, 24]">
            <q-btn fab color="primary" icon="add" @click="openCreate">
              <q-tooltip>Novo compromisso</q-tooltip>
            </q-btn>
          </q-page-sticky>

          <AppointmentDialog
            v-model="dialogOpen"
            :appointment="selectedAppointment"
            @delete="requestRemoveAppointment"
            @save="saveAppointment"
          />
          <ConfirmActionDialog
            v-model="confirmDeleteOpen"
            title="Excluir compromisso"
            message="Essa acao remove o compromisso da agenda."
            confirm-label="Excluir"
            cancel-label="Cancelar"
            @cancel="cancelRemoveAppointment"
            @confirm="confirmRemoveAppointment"
          />
        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Notify } from 'quasar'
import AppointmentCalendar from '../components/AppointmentCalendar.vue'
import AppointmentDialog from '../components/AppointmentDialog.vue'
import CalendarToolbar from '../components/CalendarToolbar.vue'
import ConfirmActionDialog from '../components/ConfirmActionDialog.vue'
import ErrorState from '../components/state/ErrorState.vue'
import LoadingState from '../components/state/LoadingState.vue'
import { useAppointmentsStore } from '../stores/appointments'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const appointments = useAppointmentsStore()
const viewMode = ref('month')
const selectedDate = ref(dateKey(new Date()))
const dialogOpen = ref(false)
const selectedAppointment = ref(null)
const appointmentPendingDelete = ref(null)
const confirmDeleteOpen = ref(false)

const periodLabel = computed(() => {
  const date = new Date(`${selectedDate.value}T12:00:00`)
  return date.toLocaleDateString('pt-BR', {
    month: 'long',
    year: 'numeric'
  })
})

onMounted(async () => {
  if (!auth.user) {
    await auth.fetchMe()
  }
  await appointments.fetchAppointments()
})

function openCreate() {
  selectedAppointment.value = {
    start_datetime: `${selectedDate.value}T09:00`,
    end_datetime: `${selectedDate.value}T10:00`
  }
  dialogOpen.value = true
}

function openCreateAt(startDateTime) {
  selectedAppointment.value = {
    start_datetime: startDateTime,
    end_datetime: addHours(startDateTime, 1)
  }
  dialogOpen.value = true
}

function openEdit(appointment) {
  selectedAppointment.value = appointment
  dialogOpen.value = true
}

async function saveAppointment(payload) {
  if (selectedAppointment.value?.id) {
    await appointments.updateAppointment(selectedAppointment.value.id, payload)
  } else {
    await appointments.createAppointment(payload)
  }
  dialogOpen.value = false
  Notify.create({ type: 'positive', message: 'Compromisso salvo.' })
}

function requestRemoveAppointment(appointment) {
  appointmentPendingDelete.value = appointment
  confirmDeleteOpen.value = true
}

function cancelRemoveAppointment() {
  confirmDeleteOpen.value = false
  appointmentPendingDelete.value = null
}

async function confirmRemoveAppointment() {
  if (!appointmentPendingDelete.value?.id) {
    return
  }

  await appointments.removeAppointment(appointmentPendingDelete.value.id)
  confirmDeleteOpen.value = false
  dialogOpen.value = false
  appointmentPendingDelete.value = null
  selectedAppointment.value = null
  Notify.create({ type: 'positive', message: 'Compromisso excluido.' })
}

function logout() {
  auth.logout()
  router.push('/login')
}

function movePeriod(direction) {
  const date = new Date(`${selectedDate.value}T12:00:00`)
  if (viewMode.value === 'day') {
    date.setDate(date.getDate() + direction)
  } else {
    date.setMonth(date.getMonth() + direction)
  }
  selectedDate.value = dateKey(date)
}

function goToday() {
  selectedDate.value = dateKey(new Date())
}

function dateKey(value) {
  const date = new Date(value)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function addHours(value, hours) {
  const date = new Date(value)
  date.setHours(date.getHours() + hours)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hour = String(date.getHours()).padStart(2, '0')
  const minute = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day}T${hour}:${minute}`
}
</script>

<style scoped>
.calendar-page {
  min-height: 100vh;
}

.calendar-shell-page {
  display: grid;
  gap: clamp(0.75rem, 2vw, 1rem);
  width: min(96vw, 78rem);
  margin: 0 auto;
  padding: clamp(0.85rem, 2.5vw, 1.35rem) 0 clamp(1rem, 3vw, 1.75rem);
}
</style>
