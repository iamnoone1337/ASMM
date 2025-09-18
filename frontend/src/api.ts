import axios from 'axios'

export async function startScan(payload: {
  domain: string
  scope?: { include?: string[]; exclude?: string[] }
  bruteforce: boolean
  resolution: boolean
  notify: boolean
  active_token?: string
}) {
  const { data } = await axios.post('/api/v1/scan', payload)
  return data
}

export async function getScanStatus(scanId: string) {
  const { data } = await axios.get(`/api/v1/scan/${scanId}`)
  return data
}

export async function listAssets(domain: string, live = false, limit = 100, offset = 0) {
  const { data } = await axios.get(`/api/v1/assets`, { params: { domain, live, limit, offset } })
  return data
}

export function exportCsvUrl(domain: string) {
  return `/api/v1/assets/export.csv?domain=${encodeURIComponent(domain)}`
}