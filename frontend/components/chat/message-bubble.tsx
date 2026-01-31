'use client'

import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Volume2, Square } from 'lucide-react'
import ReactMarkdown from 'react-markdown'

interface MessageBubbleProps {
  role: 'user' | 'model'
  content: string
  onSpeak?: () => void
  isSpeaking?: boolean
  onStopSpeak?: () => void
}

export default function MessageBubble({ role, content, onSpeak, isSpeaking, onStopSpeak }: MessageBubbleProps) {
  const isUser = role === 'user'
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-xl ${isUser ? 'order-2' : 'order-1'}`}>
        <Card className={`rounded-3xl px-6 py-4 ${isUser ? 'bg-primary text-white rounded-br-sm' : 'bg-muted text-foreground rounded-bl-sm'}`}>
          {role === 'model' && (
            <div className="flex items-start justify-between gap-3 mb-2">
              <div className="flex-1">
                <ReactMarkdown
                  className="prose text-sm prose-p:leading-relaxed"
                  components={{
                    strong: ({ node, ...props }) => <span className="text-primary font-bold" {...props} />
                  }}
                >
                  {content}
                </ReactMarkdown>
              </div>
              {onSpeak && (
                <Button size="sm" variant="ghost" onClick={isSpeaking ? onStopSpeak : onSpeak} className="text-muted-foreground hover:text-foreground">
                  {isSpeaking ? <Square className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
                </Button>
              )}
            </div>
          )}
          {role === 'user' && <p className="text-sm leading-relaxed whitespace-pre-wrap">{content}</p>}
        </Card>
      </div>
    </div>
  )
}