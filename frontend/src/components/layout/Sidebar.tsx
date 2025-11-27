'use client'
import { LayoutDashboard, FileSearch } from 'lucide-react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { SupervityIcon } from '@/components/ui/supervity-icon'

// Dummy NavLink component for demonstration
const NavLink = ({
  href,
  children,
  icon: Icon,
}: {
  href: string
  children: React.ReactNode
  icon: React.ElementType
}) => {
  const pathname = usePathname()
  const isActive = pathname === href

  return (
    <Link
      href={href}
      className={`flex items-center gap-3 rounded-lg px-4 py-3 text-sm font-medium transition-all ${
        isActive
          ? 'bg-[#000b37] text-white'
          : 'text-gray-700 hover:bg-gray-100 hover:text-[#000b37]'
      }`}
    >
      <Icon className='h-5 w-5' />
      {children}
    </Link>
  )
}

export function Sidebar() {
  return (
    <div className='hidden border-r border-gray-200 bg-white md:block'>
      <div className='flex h-full max-h-screen flex-col gap-2'>
        <div className='flex h-16 items-center border-b border-gray-200 px-6'>
          <Link href='/' className='flex items-center gap-2'>
            <SupervityIcon />
            <span className='text-lg font-semibold text-[#000b37]'>Supervity</span>
          </Link>
        </div>
        <div className='flex-1 px-3 py-4'>
          <nav className='grid gap-1'>
            <NavLink href='/' icon={LayoutDashboard}>
              Dashboard
            </NavLink>
            <NavLink href='/explorer' icon={FileSearch}>
              Invoice Explorer
            </NavLink>
          </nav>
        </div>
      </div>
    </div>
  )
}
