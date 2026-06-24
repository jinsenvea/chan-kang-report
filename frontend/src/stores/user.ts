import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getToken, setToken, removeToken, getUser, setUser, removeUser } from '@/utils/auth'
import request from '@/utils/request'

export const useUserStore = defineStore('user', () => {
  const token = ref(getToken() || '')
  const username = ref(getUser()?.username || '')
  const realName = ref(getUser()?.realName || '')

  const login = async (loginForm: { username: string; password: string }) => {
    const res: any = await request.post('/api/auth/login', loginForm)
    token.value = res.token
    username.value = res.username
    realName.value = res.realName || res.username
    setToken(res.token)
    setUser({ username: res.username, realName: realName.value })
    return res
  }

  const logout = () => {
    token.value = ''
    username.value = ''
    realName.value = ''
    removeToken()
    removeUser()
  }

  return { token, username, realName, login, logout }
})
