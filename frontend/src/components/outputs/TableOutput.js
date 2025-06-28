"use client"

/**
 * Table Output Component
 * Displays structured data in a sortable, filterable table
 */

import { useState, useMemo } from "react"

const TableOutput = ({ data }) => {
  const [sortConfig, setSortConfig] = useState({ key: null, direction: "asc" })
  const [filterText, setFilterText] = useState("")
  const [currentPage, setCurrentPage] = useState(1)
  const [rowsPerPage] = useState(10)

  const tableData = data?.tableData || { columns: [], rows: [] }
  const { columns, rows } = tableData

  // Filter and sort data
  const processedData = useMemo(() => {
    let filteredRows = rows

    // Apply filter
    if (filterText) {
      filteredRows = rows.filter((row) =>
        Object.values(row).some((value) => String(value).toLowerCase().includes(filterText.toLowerCase())),
      )
    }

    // Apply sort
    if (sortConfig.key) {
      filteredRows.sort((a, b) => {
        const aValue = a[sortConfig.key]
        const bValue = b[sortConfig.key]

        // Handle numeric values (remove currency symbols and commas)
        const aNumeric = String(aValue).replace(/[₹,]/g, "")
        const bNumeric = String(bValue).replace(/[₹,]/g, "")

        if (!isNaN(aNumeric) && !isNaN(bNumeric)) {
          return sortConfig.direction === "asc"
            ? Number(aNumeric) - Number(bNumeric)
            : Number(bNumeric) - Number(aNumeric)
        }

        // Handle string values
        if (aValue < bValue) return sortConfig.direction === "asc" ? -1 : 1
        if (aValue > bValue) return sortConfig.direction === "asc" ? 1 : -1
        return 0
      })
    }

    return filteredRows
  }, [rows, filterText, sortConfig])

  // Pagination
  const totalPages = Math.ceil(processedData.length / rowsPerPage)
  const startIndex = (currentPage - 1) * rowsPerPage
  const paginatedData = processedData.slice(startIndex, startIndex + rowsPerPage)

  const handleSort = (column) => {
    setSortConfig((prevConfig) => ({
      key: column,
      direction: prevConfig.key === column && prevConfig.direction === "asc" ? "desc" : "asc",
    }))
  }

  const handleExportCSV = () => {
    const csvContent = [
      columns.join(","),
      ...processedData.map((row) => columns.map((col) => `"${String(row[col]).replace(/"/g, '""')}"`).join(",")),
    ].join("\n")

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" })
    const link = document.createElement("a")
    const url = URL.createObjectURL(blob)
    link.setAttribute("href", url)
    link.setAttribute("download", `query-results-${new Date().toISOString().split("T")[0]}.csv`)
    link.style.visibility = "hidden"
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  if (!columns.length || !rows.length) {
    return (
      <div className="table-output-empty">
        <div className="empty-state">
          <span className="empty-icon">📋</span>
          <h3>No Table Data</h3>
          <p>No structured data available for table view.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="table-output">
      {/* Table Controls */}
      <div className="table-controls">
        <div className="table-info">
          <span className="data-count">
            📊 Showing {paginatedData.length} of {processedData.length} records
            {filterText && ` (filtered from ${rows.length} total)`}
          </span>
        </div>

        <div className="table-actions">
          <input
            type="text"
            placeholder="🔍 Filter data..."
            value={filterText}
            onChange={(e) => {
              setFilterText(e.target.value)
              setCurrentPage(1) // Reset to first page when filtering
            }}
            className="filter-input"
          />

          <button onClick={handleExportCSV} className="export-button" title="Export to CSV">
            📥 Export CSV
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              {columns.map((column) => (
                <th
                  key={column}
                  onClick={() => handleSort(column)}
                  className={`sortable ${sortConfig.key === column ? "sorted" : ""}`}
                  title={`Click to sort by ${column}`}
                >
                  <div className="header-content">
                    <span className="header-text">{column}</span>
                    <span className="sort-indicator">
                      {sortConfig.key === column ? (sortConfig.direction === "asc" ? "↑" : "↓") : "↕"}
                    </span>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paginatedData.map((row, index) => (
              <tr key={startIndex + index} className="data-row">
                {columns.map((column) => (
                  <td key={column} className="data-cell">
                    {row[column]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="pagination">
          <button
            onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
            disabled={currentPage === 1}
            className="pagination-button"
          >
            ← Previous
          </button>

          <span className="pagination-info">
            Page {currentPage} of {totalPages}
          </span>

          <button
            onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
            disabled={currentPage === totalPages}
            className="pagination-button"
          >
            Next →
          </button>
        </div>
      )}
    </div>
  )
}

export default TableOutput
