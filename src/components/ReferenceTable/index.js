import React from 'react';
import referenceData from '@site/docs/generated/reference-data.json';

function formatValue(value) {
  if (value === undefined || value === '') return '—';
  return String(value).replace(/^['"]|['"]$/g, '');
}

export default function ReferenceTable({ type, service }) {
  const rows = type === 'action'
    ? referenceData.actions[service] ?? []
    : referenceData[type] ?? [];

  return (
    <table>
      <thead>
        <tr><th>Field</th><th>Description</th><th>Default / example</th></tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.key}>
            <td><code>{row.key}</code>{row.name && row.name !== row.key ? <><br />{row.name}</> : null}</td>
            <td>{formatValue(row.description)}</td>
            <td>{formatValue(row.default ?? row.example)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
