const TOKEN_KEY = 'peer_biz_sync_token'
const USER_KEY = 'peer_biz_sync_user'
const DEMO_KEY = 'peer_biz_sync_demo'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function removeToken() {
  localStorage.removeItem(TOKEN_KEY)
}

export function getUser(): { username: string; realName: string } | null {
  const raw = localStorage.getItem(USER_KEY)
  return raw ? JSON.parse(raw) : null
}

export function setUser(user: { username: string; realName: string }) {
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export function removeUser() {
  localStorage.removeItem(USER_KEY)
}

/** 演示模式标记 */
export function setDemoMode(v: boolean) {
  if (v) localStorage.setItem(DEMO_KEY, '1')
  else localStorage.removeItem(DEMO_KEY)
}

export function isDemoMode(): boolean {
  return localStorage.getItem(DEMO_KEY) === '1'
}
