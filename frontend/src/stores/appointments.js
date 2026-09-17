import { defineStore } from 'pinia'
import { api } from '../services/api'

export const useAppointmentsStore = defineStore('appointments', {
  state: () => ({
    items: [],
    loading: false,
    error: null
  }),
  actions: {
    async fetchAppointments() {
      this.loading = true
      this.error = null
      try {
        const { data } = await api.get('/api/appointments')
        this.items = data
      } catch {
        this.error = 'Nao foi possivel carregar os compromissos.'
      } finally {
        this.loading = false
      }
    },
    async createAppointment(payload) {
      const { data } = await api.post('/api/appointments', payload)
      this.items.push(data)
    },
    async updateAppointment(id, payload) {
      const { data } = await api.put(`/api/appointments/${id}`, payload)
      this.items = this.items.map((item) => (item.id === id ? data : item))
    },
    async removeAppointment(id) {
      await api.delete(`/api/appointments/${id}`)
      this.items = this.items.filter((item) => item.id !== id)
    },
    async confirmPresence(id) {
      await api.post(`/api/appointments/${id}/confirm`)
      await this.fetchAppointments()
    },
    async unlinkMe(id, userId) {
      await api.delete(`/api/appointments/${id}/users/${userId}`)
      this.items = this.items.filter((item) => item.id !== id)
    }
  }
})
