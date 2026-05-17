'use client'

import { useState } from 'react'
import { CheckCircle2, XCircle, Upload, Download } from 'lucide-react'

export default function ExplorerPage() {
  const [files, setFiles] = useState<File[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [batchData, setBatchData] = useState(null)
  const [progress, setProgress] = useState(0)

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      // Store multiple files
      setFiles(Array.from(event.target.files))
      setProgress(0)
    }
  }

  const handleAnalyze = async () => {
    if (files.length === 0) return

    setIsLoading(true)
    setProgress(10)

    try {
      const formData = new FormData()
      
      // Append all files to FormData
      files.forEach((file) => {
        formData.append('files', file)
      })

      setProgress(30)

      const response = await fetch('/api/validate-batch', {
        method: 'POST',
        body: formData,
      })

      setProgress(70)

      if (!response.ok) {
        throw new Error('Batch validation failed')
      }

      const result = await response.json()
      setBatchData(result)
      setProgress(100)
    } catch (error) {
      console.error('Error processing batch:', error)
      setProgress(0)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDownloadReport = async () => {
    if (!batchData?.batch_report_id) return

    try {
      const response = await fetch(`/api/download-batch-report/${batchData.batch_report_id}`)
      if (!response.ok) throw new Error('Download failed')

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `batch_report_${batchData.batch_report_id}.xlsx`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error('Error downloading report:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-800 mb-2">Invoice Explorer</h1>
        <p className="text-gray-600 mb-8">Smart Batch Processing & Analytics Hub</p>

        {/* File Upload Section */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
            <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <p className="text-gray-600 mb-4">
              Drag and drop your PDF invoices here, or click to select files
            </p>
            <input
              type="file"
              multiple
              accept=".pdf,.zip"
              onChange={handleFileChange}
              className="hidden"
              id="file-input"
            />
            <label htmlFor="file-input" className="inline-block">
              <button className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 transition">
                Select Files
              </button>
            </label>
          </div>

          {files.length > 0 && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">
                Selected Files ({files.length})
              </h3>
              <ul className="space-y-2">
                {files.map((file, idx) => (
                  <li key={idx} className="text-gray-600 flex items-center">
                    <span className="mr-2">📄</span>
                    {file.name}
                  </li>
                ))}
              </ul>

              <button
                onClick={handleAnalyze}
                disabled={isLoading}
                className="mt-6 w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 transition disabled:bg-gray-400"
              >
                {isLoading ? 'Processing...' : 'Analyze Batch'}
              </button>
            </div>
          )}
        </div>

        {/* Progress Bar */}
        {isLoading && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
            <div className="flex items-center justify-between mb-2">
              <p className="text-gray-700 font-semibold">Processing invoices...</p>
              <span className="text-gray-600">{progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}

        {/* Batch Results */}
        {batchData && <BatchResultsTable batchData={batchData} onDownload={handleDownloadReport} />}
      </div>
    </div>
  )
}

function BatchResultsTable({ batchData, onDownload }) {
  return (
    <div className="bg-white rounded-lg shadow-lg p-8 space-y-6">
      {/* Summary Cards */}
      <div>
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Batch Summary</h2>
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
            <p className="text-gray-600 text-sm font-semibold">Total Processed</p>
            <p className="text-3xl font-bold text-blue-600">{batchData.summary.total_processed}</p>
          </div>
          <div className="bg-green-50 p-6 rounded-lg border border-green-200">
            <p className="text-gray-600 text-sm font-semibold">Passed</p>
            <div className="flex items-center">
              <CheckCircle2 className="h-8 w-8 text-green-600 mr-2" />
              <p className="text-3xl font-bold text-green-600">{batchData.summary.total_passed}</p>
            </div>
          </div>
          <div className="bg-red-50 p-6 rounded-lg border border-red-200">
            <p className="text-gray-600 text-sm font-semibold">Failed</p>
            <div className="flex items-center">
              <XCircle className="h-8 w-8 text-red-600 mr-2" />
              <p className="text-3xl font-bold text-red-600">{batchData.summary.total_failed}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Results Table */}
      <div>
        <h3 className="text-xl font-bold text-gray-800 mb-4">Batch Results</h3>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="bg-gray-100 border-b-2 border-gray-300">
                <th className="px-4 py-3 text-left text-gray-700 font-semibold">Filename</th>
                <th className="px-4 py-3 text-left text-gray-700 font-semibold">Invoice Number</th>
                <th className="px-4 py-3 text-left text-gray-700 font-semibold">PO Number</th>
                <th className="px-4 py-3 text-left text-gray-700 font-semibold">Status</th>
                <th className="px-4 py-3 text-left text-gray-700 font-semibold">Top Failure Reasons</th>
              </tr>
            </thead>
            <tbody>
              {batchData.results.map((result, idx) => (
                <tr key={idx} className="border-b border-gray-200 hover:bg-gray-50">
                  <td className="px-4 py-3 text-gray-800">{result.filename}</td>
                  <td className="px-4 py-3 text-gray-800">
                    {result.extraction_data?.invoice_number || 'N/A'}
                  </td>
                  <td className="px-4 py-3 text-gray-800">
                    {result.extraction_data?.po_number || 'N/A'}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold ${
                        result.status === 'passed'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {result.status === 'passed' ? (
                        <CheckCircle2 className="h-4 w-4 mr-1" />
                      ) : (
                        <XCircle className="h-4 w-4 mr-1" />
                      )}
                      {result.status.charAt(0).toUpperCase() + result.status.slice(1)}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-600 text-sm">
                    {result.validation_results?.failing_rules
                      ?.slice(0, 3)
                      .join(', ') || 'None'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Download Button */}
      <button
        onClick={onDownload}
        className="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 transition flex items-center justify-center gap-2"
      >
        <Download className="h-5 w-5" />
        Download Consolidated Excel Report
      </button>
    </div>
  )
}
