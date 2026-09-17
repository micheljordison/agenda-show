import { defineStore } from 'pinia'
import { api } from '../services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('agenda_token'),
    user: null,
    loading: false,
    error: null
  }),
  actions: {
    async login(username, password) {
      this.loading = true
      this.error = null
      try {
        const body = new URLSearchParams({ username, password })
        const { data } = await api.post('/api/auth/login', body)
        this.token = data.access_token
        localStorage.setItem('agenda_token', this.token)
        await this.fetchMe()
      } catch {
        this.token = null
        this.user = null
        localStorage.removeItem('agenda_token')
        this.error = 'Usuario ou senha invalidos.'
        throw new Error(this.error)
      } finally {
        this.loading = false
      }
    },
    async fetchMe() {
      try {
        const { data } = await api.get('/api/users/me')
        this.user = data
        return data
      } catch (error) {
        this.logout()
        throw error
      }
    },
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('agenda_token')
    }
  }
})
