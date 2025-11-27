'use client'
import Image from 'next/image'

export function SupervityIcon({ className }: { className?: string }) {
  return (
    <div className={`flex items-center justify-center ${className || 'h-8 w-8'}`}>
      <Image
        src="/supervity-favicon.png"
        alt="Supervity"
        width={32}
        height={32}
        className="h-full w-full object-contain"
      />
    </div>
  )
}

