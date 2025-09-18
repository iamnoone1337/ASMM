import React, { useState } from 'react'

const ScanForm: React.FC<{ onStart: (payload:any)=>void }> = ({ onStart }) => {
  const [domain, setDomain] = useState('example.com')
  const [bruteforce, setBruteforce] = useState(false)
  const [resolution, setResolution] = useState(false)
  const [include, setInclude] = useState('')
  const [exclude, setExclude] = useState('')
  const [activeToken, setActiveToken] = useState('')

  const submit = (e: React.FormEvent) => {
    e.preventDefault()
    onStart({
      domain,
      scope: {
        include: include ? include.split(',').map(s=>s.trim()).filter(Boolean) : undefined,
        exclude: exclude ? exclude.split(',').map(s=>s.trim()).filter(Boolean) : undefined,
      },
      bruteforce,
      resolution,
      notify: false,
      active_token: activeToken || undefined
    })
  }

  return (
    <form onSubmit={submit} style={{ display:'grid', gap: '0.5rem', gridTemplateColumns: '1fr 1fr 1fr 1fr', alignItems:'end' }}>
      <div>
        <label>Domain<br/><input value={domain} onChange={e=>setDomain(e.target.value)} placeholder="example.com"/></label>
      </div>
      <div>
        <label>Include patterns (regex, comma-separated)<br/><input value={include} onChange={e=>setInclude(e.target.value)} placeholder="^api|^dev"/></label>
      </div>
      <div>
        <label>Exclude patterns (regex, comma-separated)<br/><input value={exclude} onChange={e=>setExclude(e.target.value)} placeholder="^old|staging"/></label>
      </div>
      <div>
        <label>Active token (enables bruteforce & resolution)<br/><input value={activeToken} onChange={e=>setActiveToken(e.target.value)} placeholder="token"/></label>
      </div>
      <div>
        <label><input type="checkbox" checked={bruteforce} onChange={e=>setBruteforce(e.target.checked)} /> Bruteforce</label>
      </div>
      <div>
        <label><input type="checkbox" checked={resolution} onChange={e=>setResolution(e.target.checked)} /> Resolve DNS</label>
      </div>
      <div>
        <button type="submit">Start Scan</button>
      </div>
    </form>
  )
}
export default ScanForm