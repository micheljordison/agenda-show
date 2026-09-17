<template>
  <section class="location-picker">
    <div class="location-search-row">
      <q-input
        v-model="searchTerm"
        label="Buscar local"
        outlined
        :loading="searching"
        @keyup.enter="searchLocation"
      >
        <template #prepend>
          <q-icon name="search" />
        </template>
      </q-input>
      <q-btn color="primary" icon="search" round unelevated @click="searchLocation">
        <q-tooltip>Buscar</q-tooltip>
      </q-btn>
    </div>

    <q-list v-if="searchResults.length" bordered separator class="location-results">
      <q-item
        v-for="result in searchResults"
        :key="result.place_id"
        clickable
        @click="selectSearchResult(result)"
      >
        <q-item-section>
          <q-item-label>{{ result.display_name }}</q-item-label>
        </q-item-section>
      </q-item>
    </q-list>

    <div v-if="localName || localUrl" class="selected-location">
      <q-icon name="place" />
      <div>
        <strong>{{ localName || 'Local selecionado' }}</strong>
        <span v-if="coordinatesLabel">{{ coordinatesLabel }}</span>
      </div>
      <q-btn
        v-if="localUrl"
        class="google-maps-link"
        color="secondary"
        icon="open_in_new"
        label="Abrir no Google Maps"
        outline
        no-caps
        type="a"
        :href="localUrl"
        target="_blank"
        rel="noreferrer"
      >
      </q-btn>
    </div>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  locationName: {
    type: String,
    default: ''
  },
  latitude: {
    type: [Number, String],
    default: null
  },
  longitude: {
    type: [Number, String],
    default: null
  }
})

const emit = defineEmits([
  'update:modelValue',
  'update:locationName',
  'update:latitude',
  'update:longitude'
])

const searchTerm = ref('')
const searchResults = ref([])
const searching = ref(false)
const localName = ref(props.locationName || '')
const localUrl = ref(props.modelValue || '')
const localLatitude = ref(normalizeCoordinate(props.latitude))
const localLongitude = ref(normalizeCoordinate(props.longitude))
let searchDebounceId = null
let searchController = null

const coordinatesLabel = computed(() => {
  if (localLatitude.value === null || localLongitude.value === null) {
    return ''
  }

  return `${localLatitude.value.toFixed(6)}, ${localLongitude.value.toFixed(6)}`
})

watch(
  () => props.locationName,
  (value) => {
    localName.value = value || ''
    if (!searchTerm.value) {
      searchTerm.value = value || ''
    }
  },
  { immediate: true }
)

watch(
  () => props.modelValue,
  (value) => {
    localUrl.value = value || ''
  },
  { immediate: true }
)

watch(
  () => [props.latitude, props.longitude],
  () => {
    localLatitude.value = normalizeCoordinate(props.latitude)
    localLongitude.value = normalizeCoordinate(props.longitude)
  },
  { immediate: true }
)

watch(searchTerm, (value) => {
  clearScheduledSearch()

  if (value.trim().length < 3 || value === localName.value) {
    return
  }

  searchDebounceId = window.setTimeout(() => {
    searchLocation()
  }, 2000)
})

onBeforeUnmount(() => {
  clearScheduledSearch()
  abortCurrentSearch()
})

async function searchLocation() {
  clearScheduledSearch()
  const query = searchTerm.value.trim()
  if (query.length < 3) {
    searchResults.value = []
    return
  }

  abortCurrentSearch()
  searchController = new AbortController()
  searching.value = true
  try {
    const params = new URLSearchParams({
      q: query,
      format: 'jsonv2',
      addressdetails: '1',
      limit: '5',
      countrycodes: 'br'
    })
    const response = await fetch(`https://nominatim.openstreetmap.org/search?${params}`, {
      signal: searchController.signal
    })
    searchResults.value = await response.json()
  } catch (error) {
    if (error.name !== 'AbortError') {
      searchResults.value = []
    }
  } finally {
    searching.value = false
    searchController = null
  }
}

function selectSearchResult(result) {
  const latitude = Number(result.lat)
  const longitude = Number(result.lon)

  if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) {
    return
  }

  const name = result.display_name
  const googleMapsUrl = toGoogleMapsUrl(latitude, longitude)

  localName.value = name
  localLatitude.value = latitude
  localLongitude.value = longitude
  localUrl.value = googleMapsUrl
  searchTerm.value = name
  searchResults.value = []

  emit('update:locationName', name)
  emit('update:latitude', latitude)
  emit('update:longitude', longitude)
  emit('update:modelValue', googleMapsUrl)
}

function normalizeCoordinate(value) {
  const coordinate = Number(value)
  return Number.isFinite(coordinate) ? coordinate : null
}

function clearScheduledSearch() {
  if (searchDebounceId) {
    window.clearTimeout(searchDebounceId)
    searchDebounceId = null
  }
}

function abortCurrentSearch() {
  if (searchController) {
    searchController.abort()
    searchController = null
  }
}

function toGoogleMapsUrl(latitude, longitude) {
  return `https://www.google.com/maps/search/?api=1&query=${latitude},${longitude}`
}
</script>

<style scoped>
.location-picker {
  display: grid;
  gap: 0.75rem;
}

.location-search-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 0.65rem;
  align-items: center;
}

.location-results {
  max-height: 12rem;
  overflow: auto;
  border-color: rgb(148 163 184 / 0.32);
  border-radius: var(--radius-control);
}

.selected-location {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  gap: 0.75rem;
  align-items: center;
  border: 0.0625rem solid rgb(var(--color-secondary) / 0.24);
  border-radius: var(--radius-control);
  background: rgb(var(--color-secondary) / 0.08);
  padding: 0.75rem;
}

.selected-location > .q-icon {
  color: rgb(var(--color-secondary));
  font-size: 1.35rem;
}

.selected-location strong,
.selected-location span {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.selected-location strong {
  color: rgb(15 23 42);
}

.selected-location span {
  color: rgb(71 85 105);
  font-size: 0.82rem;
}

.google-maps-link {
  justify-self: end;
  white-space: nowrap;
}

@media (max-width: 42rem) {
  .selected-location {
    grid-template-columns: auto minmax(0, 1fr);
  }

  .google-maps-link {
    grid-column: 1 / -1;
    justify-self: stretch;
  }
}
</style>
