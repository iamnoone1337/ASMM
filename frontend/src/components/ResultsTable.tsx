import React from 'react'

const ResultsTable: React.FC<{ rows: any[] }> = ({ rows }) => {
  if (!rows.length) return null
  return (
    <div style={{ marginTop: '1rem' }}>
      <h3>Results</h3>
      <table style={{ width:'100%', borderCollapse:'collapse' }}>
        <thead>
          <tr>
            <th style={{textAlign:'left'}}>Subdomain</th>
            <th>Resolved</th>
            <th>IPs</th>
            <th>Sources</th>
            <th>First Seen</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r:any)=>(
            <tr key={r.id}>
              <td>{r.normalized}</td>
              <td>{r.resolved ? 'true' : 'false'}</td>
              <td>{(r.ips||[]).join(', ')}</td>
              <td>{(r.sources||[]).join(', ')}</td>
              <td>{r.first_seen}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
export default ResultsTable