'use client'

import { useState } from 'react'
import { CheckCircle2, XCircle, Upload, Download, FileText } from 'lucide-react'
import { AccentButton, NavyButton } from '@/components/ui/accent-button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface ValidationResult {
  rule_id: number
  rule_name: string
  status: string
  remarks: string
}

interface ValidationResponse {
  extraction_data: {
    invoice_number: string
    invoice_date: string
    vendor_name: string
    po_number: string
    total_amount: string
    tax_amount: string
    document_type: string
    irn_number?: string
    qr_code_present: boolean
    vendor_gstin?: string
  }
  linked_po_found: boolean
  linked_ses_found: boolean
  results: ValidationResult[]
  overall_status: string
  report_id?: string
}

export default function ExplorerPage() {
  // Demo Mode: No authentication required
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [validationData, setValidationData] = useState<ValidationResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]
      if (file.type !== 'application/pdf') {
        setError('Please upload a PDF file')
        return
      }
      setSelectedFile(file)
      setError(null)
      setValidationData(null)
    }
  }

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setError('Please select a PDF file')
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      // Demo Mode: No authentication token needed
      // Ensure we use port 8002 - check both env var and fallback
      let API_URL = process.env.NEXT_PUBLIC_API_URL
      
      // Validate and fix API_URL
      if (!API_URL || 
          API_URL.trim() === '' || 
          API_URL.includes(':8000') || 
          !API_URL.startsWith('http://') && !API_URL.startsWith('https://')) {
        API_URL = 'http://localhost:8002'
      }
      
      // Ensure API_URL doesn't end with a slash
      API_URL = API_URL.trim().replace(/\/+$/, '')
      
      const BASE_PATH = (process.env.NEXT_PUBLIC_BASE_PATH || '').trim()
      const fullUrl = `${API_URL}${BASE_PATH}/api/invoices/validate`

      console.log('=== Invoice Validation Request ===')
      console.log('API_URL:', API_URL)
      console.log('BASE_PATH:', BASE_PATH || '(empty)')
      console.log('Full URL:', fullUrl)
      console.log('Making request to:', fullUrl)

      const response = await fetch(fullUrl, {
        method: 'POST',
        body: formData,
        // Don't set Content-Type header - let browser set it with boundary for FormData
      })

      console.log('Response status:', response.status, response.statusText)

      if (!response.ok) {
        let errorMessage = `Server error: ${response.status} ${response.statusText}`
        try {
          const errorData = await response.json()
          errorMessage = errorData.detail || errorData.message || errorMessage
        } catch {
          // If response is not JSON, use status text
          const text = await response.text().catch(() => '')
          errorMessage = text || errorMessage
        }
        throw new Error(errorMessage)
      }

      const data: ValidationResponse = await response.json()
      setValidationData(data)
    } catch (err) {
      let errorMessage = 'Unknown error occurred'
      if (err instanceof TypeError && err.message === 'Failed to fetch') {
        let API_URL = process.env.NEXT_PUBLIC_API_URL
        if (!API_URL || 
            API_URL.trim() === '' || 
            API_URL.includes(':8000') || 
            !API_URL.startsWith('http://') && !API_URL.startsWith('https://')) {
          API_URL = 'http://localhost:8002'
        }
        API_URL = API_URL.trim().replace(/\/+$/, '')
        const BASE_PATH = (process.env.NEXT_PUBLIC_BASE_PATH || '').trim()
        const attemptedUrl = `${API_URL}${BASE_PATH}/api/invoices/validate`
        errorMessage = `Unable to connect to the server. Please ensure the backend API is running and accessible at ${attemptedUrl}. Check: 1) Backend is running on port 8002 (run: uvicorn app.main:app --reload --host 0.0.0.0 --port 8002), 2) No firewall blocking the connection, 3) CORS is properly configured.`
      } else if (err instanceof Error) {
        errorMessage = err.message
      }
      setError(errorMessage)
      console.error('Error validating invoice:', err)
      let errorAPI_URL = process.env.NEXT_PUBLIC_API_URL
      if (!errorAPI_URL || 
          errorAPI_URL.trim() === '' || 
          errorAPI_URL.includes(':8000') || 
          !errorAPI_URL.startsWith('http://') && !errorAPI_URL.startsWith('https://')) {
        errorAPI_URL = 'http://localhost:8002'
      }
      errorAPI_URL = errorAPI_URL.trim().replace(/\/+$/, '')
      const errorBASE_PATH = (process.env.NEXT_PUBLIC_BASE_PATH || '').trim()
      console.error('Attempted URL:', `${errorAPI_URL}${errorBASE_PATH}/api/invoices/validate`)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDownloadReport = async () => {
    if (!validationData?.report_id) return

    try {
      // Demo Mode: No authentication token needed
      let API_URL = process.env.NEXT_PUBLIC_API_URL
      if (!API_URL || 
          API_URL.trim() === '' || 
          API_URL.includes(':8000') || 
          !API_URL.startsWith('http://') && !API_URL.startsWith('https://')) {
        API_URL = 'http://localhost:8002'
      }
      API_URL = API_URL.trim().replace(/\/+$/, '')
      const BASE_PATH = (process.env.NEXT_PUBLIC_BASE_PATH || '').trim()
      const reportUrl = `${API_URL}${BASE_PATH}/api/invoices/report/${validationData.report_id}`

      const response = await fetch(reportUrl)

      if (!response.ok) {
        throw new Error('Failed to download report')
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `invoice_validation_report_${validationData.report_id}.xlsx`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      console.error('Error downloading report:', err)
      setError('Failed to download report. Please try again.')
    }
  }

  // Demo Mode: Always show content without authentication check
  return (
    <div className='h-full space-y-6'>
      <div>
        <h1 className='text-4xl font-bold text-gray-900'>Invoice Explorer</h1>
        <p className='mt-2 text-lg text-gray-600'>
          Upload and validate vendor invoices against purchase orders
        </p>
      </div>

      <div className='grid gap-6 lg:grid-cols-2'>
        {/* Left: Upload Section */}
        <Card className='border-0 bg-white shadow-sm'>
          <CardHeader className='border-b border-gray-100'>
            <CardTitle className='text-xl font-semibold text-gray-900'>
              Upload Invoice
            </CardTitle>
          </CardHeader>
          <CardContent className='space-y-6 p-6'>
            <div className='space-y-4'>
              <div>
                <label className='mb-2 block text-sm font-medium text-gray-700'>
                  Select PDF File
                </label>
                <div className='relative'>
                  <input
                    type='file'
                    accept='.pdf'
                    onChange={handleFileChange}
                    className='block w-full text-sm text-gray-500 file:mr-4 file:rounded-lg file:border-0 file:bg-[#000b37] file:px-4 file:py-2 file:text-sm file:font-semibold file:text-white hover:file:bg-[#1a1f3a]'
                    disabled={isLoading}
                  />
                </div>
                {selectedFile && (
                  <div className='mt-2 flex items-center gap-2 text-sm text-gray-600'>
                    <FileText className='h-4 w-4' />
                    <span>{selectedFile.name}</span>
                  </div>
                )}
              </div>

              {error && (
                <div className='rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700'>
                  {error}
                </div>
              )}

              <AccentButton
                onClick={handleAnalyze}
                disabled={!selectedFile || isLoading}
                className='w-full'
              >
                {isLoading ? (
                  <>
                    <div className='mr-2 h-4 w-4 animate-spin rounded-full border-2 border-gray-300 border-t-gray-600'></div>
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Upload className='mr-2 h-4 w-4' />
                    Analyze Invoice
                  </>
                )}
              </AccentButton>
            </div>
          </CardContent>
        </Card>

        {/* Right: Results Section */}
        <Card className='border-0 bg-white shadow-sm'>
          <CardHeader className='border-b border-gray-100'>
            <CardTitle className='text-xl font-semibold text-gray-900'>
              Validation Results
            </CardTitle>
          </CardHeader>
          <CardContent className='p-6'>
            {validationData ? (
              <div className='space-y-6'>
                {/* Header with PO/SES Status */}
                <div className='space-y-3'>
                  <div className='flex items-center gap-4'>
                    <span className='text-sm font-medium text-gray-700'>PO Linked:</span>
                    {validationData.linked_po_found ? (
                      <span className='inline-flex items-center gap-1 rounded-full bg-green-100 px-3 py-1 text-sm font-semibold text-green-800'>
                        <CheckCircle2 className='h-4 w-4' />
                        {validationData.extraction_data.po_number}
                      </span>
                    ) : (
                      <span className='inline-flex items-center gap-1 rounded-full bg-red-100 px-3 py-1 text-sm font-semibold text-red-800'>
                        <XCircle className='h-4 w-4' />
                        Not Found
                      </span>
                    )}
                  </div>
                  <div className='flex items-center gap-4'>
                    <span className='text-sm font-medium text-gray-700'>SES Linked:</span>
                    {validationData.linked_ses_found ? (
                      <span className='inline-flex items-center gap-1 rounded-full bg-green-100 px-3 py-1 text-sm font-semibold text-green-800'>
                        <CheckCircle2 className='h-4 w-4' />
                        Found
                      </span>
                    ) : (
                      <span className='inline-flex items-center gap-1 rounded-full bg-red-100 px-3 py-1 text-sm font-semibold text-red-800'>
                        <XCircle className='h-4 w-4' />
                        Not Found
                      </span>
                    )}
                  </div>
                </div>

                {/* Validation Rules Table */}
                <div className='overflow-x-auto'>
                  <table className='w-full border-collapse'>
                    <thead>
                      <tr className='border-b border-gray-200 bg-gray-50'>
                        <th className='px-4 py-3 text-left text-sm font-semibold text-gray-700'>
                          Rule Name
                        </th>
                        <th className='px-4 py-3 text-center text-sm font-semibold text-gray-700'>
                          Status
                        </th>
                        <th className='px-4 py-3 text-left text-sm font-semibold text-gray-700'>
                          Remarks
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {validationData.results.map((result) => (
                        <tr
                          key={result.rule_id}
                          className='border-b border-gray-100 hover:bg-gray-50'
                        >
                          <td className='px-4 py-3 text-sm text-gray-900'>
                            {result.rule_name}
                          </td>
                          <td className='px-4 py-3 text-center'>
                            {result.status.toLowerCase() === 'pass' ? (
                              <CheckCircle2 className='mx-auto h-5 w-5 text-green-500' />
                            ) : (
                              <XCircle className='mx-auto h-5 w-5 text-red-500' />
                            )}
                          </td>
                          <td className='px-4 py-3 text-sm text-gray-600'>{result.remarks}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Download Report Button */}
                {validationData.report_id && (
                  <div className='pt-4'>
                    <NavyButton
                      onClick={handleDownloadReport}
                      className='w-full'
                    >
                      <Download className='mr-2 h-4 w-4' />
                      Download Compliance Report
                    </NavyButton>
                  </div>
                )}
              </div>
            ) : (
              <div className='flex h-64 items-center justify-center text-gray-500'>
                <div className='text-center'>
                  <FileText className='mx-auto h-12 w-12 text-gray-400' />
                  <p className='mt-4 text-sm'>Upload and analyze an invoice to see results</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

