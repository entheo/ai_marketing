import { createStore } from 'vuex'
import axios from 'axios'

const token = localStorage.getItem('token') || ''

if (token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

export default createStore({
  state: {
    status: '',
    token: token,
    user: localStorage.getItem('username') || '',
    temp_campaign_data: {},
    self_value_report: '',
  },

  mutations: {
    auth_success(state, { token, user }) {
      state.status = 'success'
      state.token = token
      state.user = user
    },
    logout(state) {
      state.status = ''
      state.token = ''
      state.user = ''
    },
    set_temp_campaign_data(state, data) {
      state.temp_campaign_data = data
    },
    set_self_value_report(state, report) {
      state.self_value_report = report
    },
  },

  actions: {
    logIn({ commit }, user) {
      return new Promise((resolve, reject) => {
        axios({
          url: 'http://localhost:8002/account/login/',
          data: user,
          method: 'POST'
        })
          .then(resp => {
            const token = resp.data.token.access
            const user = resp.data.username

            localStorage.setItem('token', token)
            localStorage.setItem('username', user)

            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`

            commit('auth_success', { token, user })
            resolve(resp)
          })
          .catch(err => {
            localStorage.removeItem('token')
            localStorage.removeItem('username')
            reject(err)
          })
      })
    },

    logout({ commit }) {
      return new Promise((resolve) => {
        commit('logout')
        localStorage.removeItem('token')
        localStorage.removeItem('username')
        delete axios.defaults.headers.common['Authorization']
        resolve()
      })
    }
  },

  getters: {
    isLoggedIn: state => !!state.token,
    authStatus: state => state.status,
    temp_campaign_data: state => state.temp_campaign_data,
    self_value_report: state => state.self_value_report,
  }
})
