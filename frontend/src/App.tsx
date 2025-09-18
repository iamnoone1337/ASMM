import React, { useState } from 'react'
import { startScan, getScanStatus, listAssets, exportCsvUrl } from './api'
import ScanForm from './components/ScanForm'
import JobStatus from './components/JobStatus'
import ResultsTable from './components/ResultsTable'
import ExportButtons from './components/ExportButtons'

const App: React.FC = () => {
  const [scanId, setScanId] = useState<string | null>(null)
  const [job, setJob] = useState<any | null>(null)
  const [domain, setDomain] = useState<string>('example.com')
  const [assets, setAssets] = useState<any[]>([])

  const onStart = async (payload: any) => {
    const res = await startScan(payload)
    setScanId(res.scan_id)
    setDomain(payload.domain)
    pollStatus(res.scan_id)
  }

  const pollStatus = async (id: string) => {
    const poll = async () => {
      const s = await getScanStatus(id)
      setJob(s)
      if (s.status === 'completed' || s.status === 'failed') {
        const rows = await listAssets(s.domain, false, 200)
        setAssets(rows)
      } else {
        setTimeout(poll, 2000)
      }
    }
    poll()
  }

  return (
    <div style={{ maxWidth: 1100, margin: '2rem auto', fontFamily: 'system-ui, sans-serif' }}>
      <h1>ASM Subdomain Discovery</h1>
      <ScanForm onStart={onStart} />
      {job && <JobStatus job={job} />}
      <ExportButtons domain={domain} exportCsvUrl={exportCsvUrl(domain)} />
      <ResultsTable rows={assets} />
    </div>
  )
}
export default App