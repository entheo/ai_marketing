import { createStore } from 'vuex'
import axios from 'axios';

export default createStore({
  
  // State
  state: {
    status: '',
    token: localStorage.getItem('token') || '',
    user: {},
    temp_campaign_data:{},
  },

  // Mutations
  mutations: {
    auth_success(state, { token, user }){
      state.status = 'success'
      state.token = token
      state.user = user
    },
    logout(state){
      state.status = ''
      state.token = ''
    },
    set_temp_campaign_data(state,data){
        state.temp_campaign_data=data
        },
  },

  // Actions
  actions: {
    logIn({ commit }, user) {
      return new Promise((resolve, reject) => {
        console.log(user)
        axios({ url: 'http://localhost:8005/account/login/', data: user, method: 'POST' })
        .then(resp => {
          console.log(resp)
          const token = resp.data.token.access
          const user = resp.data.username
          localStorage.setItem('token', token)
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
          commit('auth_success', { token, user })
          resolve(resp)
        })
        .catch(err => {
          localStorage.removeItem('token')
          reject(err)
        })
      })
    },
    logout({ commit }){
      return new Promise((resolve) => {
        commit('logout')
        localStorage.removeItem('token')
        delete axios.defaults.headers.common['Authorization']
        resolve()
      })
    }
  },
  getters: {
    isLoggedIn: state => !!state.token,
    authStatus: state => state.status,
    temp_campaign_data: state => state.temp_campaign_data,
  }
});
