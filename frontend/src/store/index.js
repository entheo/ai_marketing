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
    first_question_loading:false,
    first_question_ready:false,
    first_question_data:null,
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
    set_first_question_loading(state, loading) {
        state.first_question_loading = loading
        },

    set_first_question_ready(state, ready) {
        state.first_question_ready = ready
        },
    
    set_first_question_data(state, question) {
        state.first_question_data = question
        },
    
    reset_first_question(state) {
        state.first_question_loading = false
        state.first_question_ready = false
        state.first_question_data = null
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

    register(_, userData) {
      return new Promise((resolve, reject) => {
        axios({
          url: 'http://localhost:8002/account/register/',
          data: userData,
          method: 'POST'
        })
          .then(resp => {
            resolve(resp)
          })
          .catch(err => {
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
    },
checkAuth({ commit, state }) {
  return new Promise((resolve, reject) => {
    if (!state.token) {
      reject(new Error('没有 token'))
      return
    }

    axios({
      url: 'http://localhost:8002/account/auth/',
      method: 'GET'
    })
      .then(resp => {
        const user = resp.data.username
        localStorage.setItem('username', user)
        commit('auth_success', { token: state.token, user })
        resolve(resp)
      })
      .catch(err => {
        commit('logout')
        localStorage.removeItem('token')
        localStorage.removeItem('username')
        delete axios.defaults.headers.common['Authorization']
        reject(err)
      })
  })
},

prefetchFirstQuestion({ commit, state }) {
  if (state.first_question_ready && state.first_question_data) {
    return Promise.resolve(state.first_question_data)
  }

  if (state.first_question_loading) {
    return new Promise((resolve) => {
      const timer = setInterval(() => {
        if (state.first_question_ready && state.first_question_data) {
          clearInterval(timer)
          resolve(state.first_question_data)
        }
      }, 50)
    })
  }

  commit('set_first_question_loading', true)

  return fetch('http://127.0.0.1:8002/api/advice/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      type: 'self_value',
      mode: 'self_value',
      stage: 'start'
    })
  })
    .then(async (response) => {
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || '请求失败')
      }

      commit('set_first_question_data', data)
      commit('set_first_question_ready', true)
      return data
    })
    .finally(() => {
      commit('set_first_question_loading', false)
    })
},
  },

  getters: {
    isLoggedIn: state => !!state.token,
    authStatus: state => state.status,
    temp_campaign_data: state => state.temp_campaign_data,
    self_value_report: state => state.self_value_report,
    first_question_loading: state => state.first_question_loading,
    first_question_ready: state => state.first_question_ready,
    first_question_data: state => state.first_question_data,
  }
})
