'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  TrendingUp,
  FileText,
  DollarSign,
  CheckCircle2,
  Clock,
  AlertTriangle,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts'

// KPI Card Component
const KPICard = ({
  title,
  value,
  change,
  changeType,
  icon: Icon,
  color,
}: {
  title: string
  value: string
  change?: string
  changeType?: 'up' | 'down'
  icon: React.ElementType
  color: string
}) => (
  <Card className='border-0 bg-white shadow-sm transition-shadow hover:shadow-md'>
    <CardContent className='p-6'>
      <div className='flex items-center justify-between'>
        <div className='space-y-2'>
          <p className='text-sm font-medium text-gray-600'>{title}</p>
          <p className='text-3xl font-bold text-gray-900'>{value}</p>
          {change && (
            <div className='flex items-center gap-1 text-sm'>
              {changeType === 'up' ? (
                <ArrowUpRight className='h-4 w-4 text-green-600' />
              ) : (
                <ArrowDownRight className='h-4 w-4 text-red-600' />
              )}
              <span
                className={
                  changeType === 'up' ? 'text-green-600' : 'text-red-600'
                }
              >
                {change}
              </span>
              <span className='text-gray-500'>vs last month</span>
            </div>
          )}
        </div>
        <div className={`rounded-2xl ${color} p-4`}>
          <Icon className='h-8 w-8 text-white' />
        </div>
      </div>
    </CardContent>
  </Card>
)

// Status Card Component
const StatusCard = ({
  title,
  count,
  percentage,
  icon: Icon,
  color,
}: {
  title: string
  count: number
  percentage: number
  icon: React.ElementType
  color: string
}) => (
  <Card className='border-0 bg-white shadow-sm'>
    <CardContent className='p-6'>
      <div className='flex items-center justify-between'>
        <div className='space-y-1'>
          <div className='flex items-center gap-2'>
            <Icon className={`h-5 w-5 ${color}`} />
            <p className='text-sm font-medium text-gray-600'>{title}</p>
          </div>
          <p className='text-2xl font-bold text-gray-900'>{count}</p>
          <p className='text-xs text-gray-500'>{percentage}% of total</p>
        </div>
      </div>
    </CardContent>
  </Card>
)

// Sample data for charts
const invoiceTrendData = [
  { month: 'Jan', processed: 120, approved: 102, rejected: 18 },
  { month: 'Feb', processed: 135, approved: 118, rejected: 17 },
  { month: 'Mar', processed: 148, approved: 130, rejected: 18 },
  { month: 'Apr', processed: 162, approved: 142, rejected: 20 },
  { month: 'May', processed: 175, approved: 155, rejected: 20 },
  { month: 'Jun', processed: 189, approved: 168, rejected: 21 },
]

const approvalRateData = [
  { name: 'Auto-Approved', value: 85, color: '#85c20b' },
  { name: 'Manual Review', value: 10, color: '#000b37' },
  { name: 'Rejected', value: 5, color: '#ef4444' },
]

const vendorPerformanceData = [
  { vendor: 'Vendor A', invoices: 45, accuracy: 98 },
  { vendor: 'Vendor B', invoices: 38, accuracy: 95 },
  { vendor: 'Vendor C', invoices: 32, accuracy: 92 },
  { vendor: 'Vendor D', invoices: 28, accuracy: 89 },
  { vendor: 'Vendor E', invoices: 22, accuracy: 87 },
]

export default function HomePage() {
  // Demo Mode: Always show Dashboard content without authentication check
  return (
    <div className='space-y-8'>
      {/* Welcome Section */}
      <div>
        <h1 className='text-4xl font-bold text-gray-900'>
          Invoice Command Center
        </h1>
        <p className='mt-2 text-lg text-gray-600'>
          Automated 3-Way Match validation for Accounts Payable
        </p>
      </div>

      {/* KPI Cards */}
      <div className='grid gap-6 md:grid-cols-4'>
        <KPICard
          title='Auto-Approval Rate'
          value='89%'
          change='+4%'
          changeType='up'
          icon={TrendingUp}
          color='bg-[#85c20b]'
        />
        <KPICard
          title='Total Processed'
          value='1,247'
          change='+12%'
          changeType='up'
          icon={FileText}
          color='bg-[#000b37]'
        />
        <KPICard
          title='Total Value'
          value='$2.4M'
          change='+8%'
          changeType='up'
          icon={DollarSign}
          color='bg-blue-500'
        />
        <KPICard
          title='Avg Processing Time'
          value='2.3h'
          change='-15%'
          changeType='down'
          icon={Clock}
          color='bg-purple-500'
        />
      </div>

      {/* Status Overview Cards */}
      <div className='grid gap-6 md:grid-cols-4'>
        <StatusCard
          title='Approved'
          count={1110}
          percentage={89}
          icon={CheckCircle2}
          color='text-green-600'
        />
        <StatusCard
          title='Pending Review'
          count={125}
          percentage={10}
          icon={Clock}
          color='text-yellow-600'
        />
        <StatusCard
          title='Rejected'
          count={62}
          percentage={5}
          icon={AlertTriangle}
          color='text-red-600'
        />
        <StatusCard
          title='In Progress'
          count={12}
          percentage={1}
          icon={FileText}
          color='text-blue-600'
        />
      </div>

      {/* Charts Section */}
      <div className='grid gap-6 lg:grid-cols-2'>
        {/* Invoice Processing Trend */}
        <Card className='border-0 bg-white shadow-sm'>
          <CardHeader>
            <CardTitle className='text-xl font-semibold text-gray-900'>
              Invoice Processing Trend
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width='100%' height={300}>
              <LineChart data={invoiceTrendData}>
                <CartesianGrid strokeDasharray='3 3' />
                <XAxis dataKey='month' />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type='monotone'
                  dataKey='processed'
                  stroke='#000b37'
                  strokeWidth={2}
                  name='Processed'
                />
                <Line
                  type='monotone'
                  dataKey='approved'
                  stroke='#85c20b'
                  strokeWidth={2}
                  name='Approved'
                />
                <Line
                  type='monotone'
                  dataKey='rejected'
                  stroke='#ef4444'
                  strokeWidth={2}
                  name='Rejected'
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Approval Rate Distribution */}
        <Card className='border-0 bg-white shadow-sm'>
          <CardHeader>
            <CardTitle className='text-xl font-semibold text-gray-900'>
              Approval Rate Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width='100%' height={300}>
              <PieChart>
                <Pie
                  data={approvalRateData}
                  cx='50%'
                  cy='50%'
                  labelLine={false}
                  label={({ name, percent }) =>
                    `${name} ${percent ? (percent * 100).toFixed(0) : 0}%`
                  }
                  outerRadius={100}
                  fill='#8884d8'
                  dataKey='value'
                >
                  {approvalRateData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Vendor Performance Chart */}
      <Card className='border-0 bg-white shadow-sm'>
        <CardHeader>
          <CardTitle className='text-xl font-semibold text-gray-900'>
            Top Vendor Performance
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width='100%' height={300}>
            <BarChart data={vendorPerformanceData}>
              <CartesianGrid strokeDasharray='3 3' />
              <XAxis dataKey='vendor' />
              <YAxis yAxisId='left' orientation='left' stroke='#000b37' />
              <YAxis
                yAxisId='right'
                orientation='right'
                stroke='#85c20b'
                domain={[0, 100]}
              />
              <Tooltip />
              <Legend />
              <Bar
                yAxisId='left'
                dataKey='invoices'
                fill='#000b37'
                name='Invoices'
              />
              <Bar
                yAxisId='right'
                dataKey='accuracy'
                fill='#85c20b'
                name='Accuracy %'
              />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  )
}
