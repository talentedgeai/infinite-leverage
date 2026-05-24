'use client'

import { useCheckoutSession } from '@/lib/billing/queries'

interface UpgradeButtonProps {
  priceId: string
  label?: string
  className?: string
}

export function UpgradeButton({
  priceId,
  label = 'Upgrade',
  className,
}: UpgradeButtonProps) {
  const checkout = useCheckoutSession()

  return (
    <button
      type="button"
      disabled={checkout.isPending}
      onClick={() => checkout.mutate({ priceId })}
      className={className}
      aria-busy={checkout.isPending}
    >
      {checkout.isPending ? 'Redirecting…' : label}
    </button>
  )
}
