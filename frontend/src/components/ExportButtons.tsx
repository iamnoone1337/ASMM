import React from 'react'

const ExportButtons: React.FC<{ domain: string, exportCsvUrl: string }> = ({ domain, exportCsvUrl }) => {
  if (!domain) return null
  return (
    <div style={{ marginTop: '0.5rem' }}>
      <a href={exportCsvUrl} target="_blank" rel="noreferrer">
        <button>Export CSV</button>
      </a>
    </div>
  )
}
export default ExportButtons