'use client'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'

const QUESTIONS = [
  'I am 30 years old, earning 50 lakhs, non-smoker.',
  'I have 25 lakh in loans and earn 80 lakh per year.',
  'Show me return of premium plans.'
]

export default function SampleQuestionsCard({ onSelect }: { onSelect: (q: string) => void }) {
  return (
    <Card className="border-border bg-card p-6 space-y-4">
      <h3 className="text-sm font-semibold text-primary">Try asking:</h3>
      <div className="space-y-2">
        {QUESTIONS.map((q, i) => (
          <Button key={i} onClick={() => onSelect(q)} variant="outline" className="w-full justify-start text-left h-auto py-3 px-4 text-sm">
            {q}
          </Button>
        ))}
      </div>
    </Card>
  )
}