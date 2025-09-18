import React from 'react'

const JobStatus: React.FC<{ job: any }> = ({ job }) => {
  return (
    <div style={{ margin: '1rem 0' }}>
      <h3>Scan Status</h3>
      <div>Status: <b>{job.status}</b></div>
      <div>Scan ID: <code>{job.id}</code></div>
      <table style={{ width:'100%', marginTop:'0.5rem', borderCollapse:'collapse' }}>
        <thead><tr><th style={{textAlign:'left'}}>Connector</th><th>Status</th><th>Started</th><th>Finished</th><th>Error</th></tr></thead>
        <tbody>
          {job.jobs.map((j:any) => (
            <tr key={j.connector}>
              <td>{j.connector}</td>
              <td>{j.status}</td>
              <td>{j.started_at || ''}</td>
              <td>{j.finished_at || ''}</td>
              <td style={{color:'crimson'}}>{j.error || ''}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
export default JobStatus