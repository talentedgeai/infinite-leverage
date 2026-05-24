'use client'

import { UpgradeButton } from './UpgradeButton'

interface PricingCardProps {
  plan: string
  price: number
  currency: string
  interval: 'month' | 'year'
  features: string[]
  priceId: string
  highlighted?: boolean
}

// TODO: Replace Tailwind classes with your project design system tokens.
export function PricingCard({
  plan,
  price,
  currency,
  interval,
  features,
  priceId,
  highlighted = false,
}: PricingCardProps) {
  const formattedPrice = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
  }).format(price)

  return (
    <div
      className={[
        'rounded-2xl border p-8 flex flex-col gap-6',
        highlighted
          ? 'border-primary bg-primary/5 shadow-lg'
          : 'border-border bg-card',
      ].join(' ')}
    >
      {/* Plan name */}
      <div>
        <p className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
          {plan}
        </p>
        <div className="mt-2 flex items-baseline gap-1">
          <span className="text-4xl font-bold tracking-tight">{formattedPrice}</span>
          <span className="text-sm text-muted-foreground">/{interval}</span>
        </div>
      </div>

      {/* Feature list */}
      <ul className="flex flex-col gap-3 flex-1">
        {features.map((feature) => (
          <li key={feature} className="flex items-start gap-2 text-sm">
            <svg
              className="mt-0.5 h-4 w-4 shrink-0 text-primary"
              viewBox="0 0 16 16"
              fill="none"
              aria-hidden="true"
            >
              <path
                d="M3 8l3.5 3.5L13 4.5"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            {feature}
          </li>
        ))}
      </ul>

      {/* CTA */}
      <UpgradeButton
        priceId={priceId}
        label={`Get ${plan}`}
        className={[
          'w-full rounded-lg px-4 py-2.5 text-sm font-semibold transition-colors',
          highlighted
            ? 'bg-primary text-primary-foreground hover:bg-primary/90'
            : 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
        ].join(' ')}
      />
    </div>
  )
}
