<template>
  <section class="calendar-shell app-panel">
    <QCalendarDay
      v-if="viewMode === 'day'"
      v-model="calendarDate"
      class="appointment-qcalendar appointment-qcalendar-week"
      view="day"
      locale="pt-BR"
      animated
      bordered
      focusable
      hoverable
      hour24-format
      no-active-date
      date-align="left"
      short-weekday-label
      :max-days="1"
      :weekdays="weekdays"
      :interval-minutes="60"
      :interval-count="14"
      :interval-start="7"
      :interval-height="52"
      @click-date="handleDateClick"
      @click-interval="handleIntervalClick"
    >
      <template #head-weekday-label="slotProps">
        <span class="calendar-weekday-letter">{{ weekdayLetter(slotProps) }}</span>
      </template>

      <template #head-day-event="slotProps">
        <button class="calendar-week-add" type="button" @click.stop="emitCreateForSlot(slotProps)">
          <q-icon name="add" />
          <q-tooltip>Novo compromisso</q-tooltip>
        </button>
      </template>

      <template #day-body="slotProps">
        <div class="calendar-week-body-events">
          <button
            v-for="appointment in appointmentsForSlot(slotProps)"
            :key="appointment.id"
            type="button"
            class="calendar-week-event-block"
            :style="weekEventStyle(appointment, slotProps)"
            @click.stop="$emit('edit', appointment)"
          >
            <strong>{{ appointment.title }}</strong>
            <span>{{ timeLabel(appointment.start_datetime) }} - {{ timeLabel(appointment.end_datetime) }}</span>
          </button>
        </div>
      </template>
    </QCalendarDay>

    <QCalendarMonth
      v-else
      v-model="calendarDate"
      class="appointment-qcalendar"
      locale="pt-BR"
      animated
      bordered
      focusable
      hoverable
      no-active-date
      date-align="left"
      enable-outside-days
      short-weekday-label
      :weekdays="weekdays"
      :day-min-height="128"
      :day-height="0"
      @click-date="handleDateClick"
    >
      <template #head-weekday-label="slotProps">
        <span class="calendar-weekday-letter">{{ weekdayLetter(slotProps) }}</span>
      </template>

      <template #day="slotProps">
        <div
          class="calendar-day-content"
          :data-outside="slotProps?.scope?.outside"
          :data-selected="slotDate(slotProps) === calendarDate"
          @click="selectSlotDate(slotProps)"
        >
          <span class="calendar-day-head">
            <span class="calendar-day-number">{{ slotProps?.scope?.timestamp?.day }}</span>
            <button class="calendar-day-add" type="button" @click.stop="emitCreateForSlot(slotProps)">
              <q-icon name="add" />
              <q-tooltip>Novo compromisso</q-tooltip>
            </button>
          </span>

          <span class="calendar-day-events">
            <button
              v-for="appointment in appointmentsForSlot(slotProps).slice(0, 3)"
              :key="appointment.id"
              type="button"
              class="calendar-event-pill"
              @click.stop="$emit('edit', appointment)"
            >
              <strong>{{ timeLabel(appointment.start_datetime) }}</strong>
              {{ appointment.title }}
            </button>
            <em v-if="appointmentsForSlot(slotProps).length > 3">
              +{{ appointmentsForSlot(slotProps).length - 3 }}
            </em>
          </span>
        </div>
      </template>
    </QCalendarMonth>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { QCalendarDay } from '@quasar/quasar-ui-qcalendar/src/QCalendarDay'
import { QCalendarMonth } from '@quasar/quasar-ui-qcalendar/src/QCalendarMonth'
import '@quasar/quasar-ui-qcalendar/src/QCalendarDay.scss'
import '@quasar/quasar-ui-qcalendar/src/QCalendarMonth.scss'

const props = defineProps({
  appointments: {
    type: Array,
    required: true
  },
  viewMode: {
    type: String,
    required: true
  },
  modelValue: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['update:modelValue', 'select-date', 'create-date', 'edit'])
const weekdays = [0, 1, 2, 3, 4, 5, 6]

const calendarDate = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const appointmentsByDate = computed(() => {
  return props.appointments.reduce((grouped, appointment) => {
    const key = dateKey(appointment.start_datetime)
    grouped[key] = [...(grouped[key] || []), appointment]
    return grouped
  }, {})
})

function appointmentsForSlot(slotProps) {
  const date = slotDate(slotProps)
  if (!date) {
    return []
  }

  return sortAppointments(appointmentsByDate.value[date] || [])
}

function sortAppointments(items) {
  return [...items].sort((first, second) => {
    return new Date(first.start_datetime).getTime() - new Date(second.start_datetime).getTime()
  })
}

function slotDate(slotProps) {
  return slotProps?.timestamp?.date || slotProps?.scope?.timestamp?.date || slotProps?.scope?.date || null
}

function weekdayLetter(slotProps) {
  const weekday = Number(slotProps?.scope?.timestamp?.weekday ?? 0)
  return ['D', 'S', 'T', 'Q', 'Q', 'S', 'S'][weekday] || ''
}

function selectSlotDate(slotProps) {
  const date = slotDate(slotProps)
  if (date) {
    calendarDate.value = date
    emit('select-date', date)
  }
}

function emitCreateForSlot(slotProps) {
  const date = slotDate(slotProps)
  if (date) {
    calendarDate.value = date
    emit('create-date', `${date}T09:00`)
  }
}

function handleDateClick(payload) {
  const date = slotDate(payload)
  if (date) {
    calendarDate.value = date
    emit('select-date', date)
  }
}

function handleIntervalClick(payload) {
  const date = slotDate(payload)
  const time = payload?.scope?.time || payload?.time || '09:00'
  if (date) {
    calendarDate.value = date
    emit('create-date', `${date}T${String(time).slice(0, 5)}`)
  }
}

function dateKey(value) {
  const date = new Date(value)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function eventDurationMinutes(appointment) {
  const duration = (new Date(appointment.end_datetime).getTime() - new Date(appointment.start_datetime).getTime()) / 60000
  return Math.max(duration, 30)
}

function calendarTime(value) {
  const date = new Date(value)
  return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

function weekEventStyle(appointment, slotProps) {
  const scope = slotProps?.scope || {}
  const timeStartPos = scope.timeStartPos
  const timeDurationHeight = scope.timeDurationHeight

  if (typeof timeStartPos !== 'function' || typeof timeDurationHeight !== 'function') {
    return {}
  }

  const top = timeStartPos(calendarTime(appointment.start_datetime), true)
  return {
    top: `${top === false ? 0 : top}px`,
    height: `${Math.max(timeDurationHeight(eventDurationMinutes(appointment)), 30)}px`
  }
}

function timeLabel(value) {
  return new Date(value).toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.calendar-shell {
  min-height: min(80vh, 50rem);
  overflow: auto;
  padding: clamp(0.75rem, 2vw, 1.1rem);
  border: 0;
  background: rgb(var(--color-surface) / 0.96);
}

.appointment-qcalendar {
  min-width: 100%;
  min-height: min(76vh, 46rem);
  overflow: hidden;
  border: 0;
  border-radius: calc(var(--radius-app) + 0.35rem);
  background: rgb(var(--color-surface));
  box-shadow: none;
}

.calendar-weekday-letter {
  display: inline-grid;
  width: 100%;
  place-items: center;
  color: rgb(82 82 91);
  font-size: 0.92rem;
  font-weight: 800;
  line-height: 1;
}

.calendar-day-content {
  display: grid;
  grid-template-rows: auto 1fr;
  gap: 0.45rem;
  min-height: 100%;
  padding: 0.4rem;
  border-radius: 1.35rem;
  cursor: pointer;
  transition: outline-color 160ms ease, background 160ms ease, opacity 160ms ease;
}

.calendar-day-content:hover,
.calendar-day-content[data-selected='true'] {
  background: rgb(var(--color-primary) / 0.04);
  outline: 0.125rem solid rgb(var(--color-secondary) / 0.9);
  outline-offset: -0.125rem;
}

.calendar-day-content[data-outside='true'] {
  opacity: 0.46;
}

.calendar-day-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.calendar-day-number {
  display: inline-grid;
  min-width: 1.7rem;
  min-height: 1.7rem;
  place-items: center;
  border-radius: 999rem;
  color: rgb(39 39 42);
  font-weight: 800;
}

.calendar-day-content[data-selected='true'] .calendar-day-number {
  background: rgb(var(--color-secondary));
  color: rgb(255 255 255);
}

.calendar-day-add,
.calendar-week-add {
  display: inline-grid;
  width: 1.9rem;
  height: 1.9rem;
  place-items: center;
  border: 0;
  border-radius: 999rem;
  background: transparent;
  color: rgb(var(--color-secondary));
  cursor: pointer;
  opacity: 0;
  transition: opacity 160ms ease, background 160ms ease;
}

.calendar-day-content:hover .calendar-day-add,
.calendar-week-add:hover {
  opacity: 1;
  background: rgb(var(--color-secondary) / 0.1);
}

.calendar-day-events {
  display: grid;
  align-content: start;
  gap: 0.3rem;
}

.calendar-event-pill,
.calendar-week-event-block {
  width: 100%;
  border: 0;
  background: rgb(var(--color-secondary));
  color: rgb(255 255 255);
  cursor: pointer;
  font-size: 0.75rem;
  line-height: 1.25;
  text-align: left;
  box-shadow: none;
}

.calendar-event-pill {
  min-height: 1.75rem;
  padding: 0.3rem 0.55rem;
  overflow: hidden;
  border-radius: 999rem;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.calendar-event-pill strong {
  margin-right: 0.25rem;
}

.calendar-day-events em {
  color: rgb(var(--color-secondary));
  font-size: 0.75rem;
  font-style: normal;
  font-weight: 800;
}

.calendar-week-body-events {
  position: relative;
  min-height: 100%;
  margin-inline: 0.25rem;
}

.calendar-week-event-block {
  position: absolute;
  inset-inline: 0.2rem;
  z-index: 2;
  display: grid;
  align-content: start;
  gap: 0.15rem;
  min-height: 1.9rem;
  padding: 0.45rem 0.6rem;
  overflow: hidden;
  border-radius: 1rem;
}

.calendar-week-event-block strong,
.calendar-week-event-block span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.calendar-week-event-block span {
  opacity: 0.86;
}

@media (max-width: 48rem) {
  .calendar-shell {
    min-height: calc(100vh - 5.25rem);
    padding: 0.65rem;
    border-radius: calc(var(--radius-app) + 0.75rem);
    margin-inline: 0;
  }

  .appointment-qcalendar {
    min-width: 100%;
    min-height: calc(100vh - 7rem);
  }

  .calendar-day-content {
    padding: 0.28rem;
  }

  .calendar-event-pill {
    min-height: 1.45rem;
    padding: 0.18rem 0.35rem;
    font-size: 0.68rem;
  }
}
</style>
