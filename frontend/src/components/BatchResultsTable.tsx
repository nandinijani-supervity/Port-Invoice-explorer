import { CheckCircle2, XCircle, Download } from 'lucide-react'
import { ReactNode } from 'react'

interface ValidationResult {
  filename: string
  status: 'passed' | 'failed'
  extraction_data?: {
    invoice_number?: string
    po_number?: string
    vendor_name?: string
    total_amount?: string
  }
  validation_results?: {
    failing_rules?: string[]
  }
}

interface BatchData {
  batch_id: string
  batch_report_id: string
  summary: {
    total_processed: number
    total_passed: number
    total_failed: number
  }
  results: ValidationResult[]
}

interface BatchResultsTableProps {
  batchData: BatchData
  onDownload?: () => void
}

export function BatchResultsTable({
  batchData,
  onDownload,
}: BatchResultsTableProps): ReactNode {
  const { summary, results } = batchData

  return (
    <div className="space-y-4">
      {/* Summary Cards (Pass/Fail metrics) */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
          <p className="text-gray-600 text-sm font-semibold">Total Processed</p>
          <p className="text-3xl font-bold text-blue-600">{summary.total_processed}</p>
        </div>
        <div className="bg-green-50 p-6 rounded-lg border border-green-200">
          <p className="text-gray-600 text-sm font-semibold">Passed</p>
          <div className="flex items-center">
            <CheckCircle2 className="h-8 w-8 text-green-600 mr-2" />
            <p className="text-3xl font-bold text-green-600">{summary.total_passed}</p>
          </div>
        </div>
        <div className="bg-red-50 p-6 rounded-lg border border-red-200">
          <p className="text-gray-600 text-sm font-semibold">Failed</p>
          <div className="flex items-center">
            <XCircle className="h-8 w-8 text-red-600 mr-2" />
            <p className="text-3xl font-bold text-red-600">{summary.total_failed}</p>
          </div>
        </div>
      </div>

      {/* Data Table */}
      <div className="overflow-x-auto border border-gray-200 rounded-lg">
        <table className="w-full">
          <thead>
            <tr className="bg-gray-100 border-b border-gray-300">
              <th className="px-4 py-3 text-left text-gray-700 font-semibold">Filename</th>
              <th className="px-4 py-3 text-left text-gray-700 font-semibold">Invoice #</th>
              <th className="px-4 py-3 text-left text-gray-700 font-semibold">PO #</th>
              <th className="px-4 py-3 text-left text-gray-700 font-semibold">Status</th>
              <th className="px-4 py-3 text-left text-gray-700 font-semibold">Failing Rules</th>
            </tr>
          </thead>
          <tbody>
            {results.map((invoice, index) => (
              <tr key={index} className="border-b border-gray-200 hover:bg-gray-50">
                <td className="px-4 py-3 text-gray-800 text-sm">{invoice.filename}</td>
                <td className="px-4 py-3 text-gray-800 text-sm">
                  {invoice.extraction_data?.invoice_number || 'N/A'}
                </td>
                <td className="px-4 py-3 text-gray-800 text-sm">
                  {invoice.extraction_data?.po_number || 'N/A'}
                </td>
                <td className="px-4 py-3 text-sm">
                  <span
                    className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${
                      invoice.status === 'passed'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {invoice.status === 'passed' ? (
                      <CheckCircle2 className="h-4 w-4 mr-1" />
                    ) : (
                      <XCircle className="h-4 w-4 mr-1" />
                    )}
                    {invoice.status === 'passed' ? 'Pass' : 'Fail'}
                  </span>
                </td>
                <td className="px-4 py-3 text-gray-600 text-sm">
                  {invoice.validation_results?.failing_rules
                    ?.slice(0, 3)
                    .join(', ') || 'None'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Download Button */}
      {onDownload && (
        <button
          onClick={onDownload}
          className="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 transition flex items-center justify-center gap-2"
        >
          <Download className="h-5 w-5" />
          Download Consolidated Excel Report
        </button>
      )}
    </div>
  )
}
