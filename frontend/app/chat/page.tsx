'use client'

import { useState, useRef, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Card } from '@/components/ui/card'
import { MessageCircle, Mic, Send, ArrowLeft, Volume2, VolumeX, Loader2 } from 'lucide-react'
import Image from 'next/image'
import { useChatBot } from '@/hooks/use-chatbot'
import { useSpeech } from '@/hooks/use-speech'
import MessageBubble from '@/components/chat/message-bubble'
import SampleQuestionsCard from '@/components/chat/sample-questions'

export default function ChatPage() {
  const router = useRouter()
  const [input, setInput] = useState('')
  const [isListening, setIsListening] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const {
    messages,
    sendMessage,
    recommendations,
    loadingIndicator,
  } = useChatBot()

  const {
    speak,
    stopSpeaking,
    isSpeaking,
  } = useSpeech()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, loadingIndicator])

  const handleSendMessage = async () => {
    if (!input.trim()) return
    const userMessage = input.trim()
    setInput('')
    await sendMessage(userMessage)
  }

  const handleStartListening = async () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert('Speech recognition is not supported in your browser')
      return
    }

    setIsListening(true)
    const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition
    const recognition = new SpeechRecognition()

    recognition.onstart = () => setIsListening(true)
    recognition.onend = () => setIsListening(false)
    recognition.onresult = (event: any) => {
      let transcript = ''
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript
      }
      setInput(transcript)
    }
    recognition.start()
  }

  const handleSampleQuestion = async (question: string) => {
    setInput('')
    await sendMessage(question)
  }

  return (
    <div className="flex flex-col h-screen bg-background">
      <div className="border-b border-border bg-card sticky top-0 z-40">
        <div className="flex h-20 items-center justify-between px-6">
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="icon" onClick={() => router.push('/')} className="hover:bg-primary/10">
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div className="flex items-center gap-2 ml-[5px]">
              <Image
                src="/share_india_logo_new.png"
                alt="Share India Logo"
                width={175}
                height={75}
                className="h-[75px] w-[175px] object-contain"
                priority
              />
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={() => setIsMuted(!isMuted)} className="hover:bg-primary/10">
            {isMuted ? <VolumeX className="h-5 w-5 text-muted-foreground" /> : <Volume2 className="h-5 w-5 text-accent" />}
          </Button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-8 scroll-smooth">
        <div className="max-w-2xl mx-auto space-y-6">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full space-y-8 py-20">
              <div className="text-center space-y-4">
                <div className="h-16 w-16 mx-auto rounded-2xl bg-gradient-to-br from-blue-600 to-sky-400 flex items-center justify-center">
                  <MessageCircle className="h-8 w-8 text-white" />
                </div>
                <h2 className="text-2xl font-bold text-primary">Welcome to InsureBot</h2>
                <p className="text-muted-foreground max-w-md">I'm your AI-powered insurance advisor. Let's find the perfect term life insurance plan for you.</p>
              </div>

              {/* Input Area for Empty State */}
              <div className="w-full max-w-2xl">
                <div className="flex gap-3">
                  <Textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSendMessage(); } }}
                    placeholder="Type your question or click the mic to speak..."
                    className="resize-none max-h-32 bg-input border-border focus:border-accent"
                  />
                  <div className="flex flex-col gap-2">
                    <Button size="icon" onClick={handleStartListening} className={`${isListening ? 'bg-red-500 animate-pulse' : 'bg-primary'}`}>
                      <Mic className="h-5 w-5" />
                    </Button>
                    <Button size="icon" onClick={handleSendMessage} disabled={!input.trim()} className="bg-accent hover:bg-emerald-600">
                      <Send className="h-5 w-5" />
                    </Button>
                  </div>
                </div>
              </div>

              <SampleQuestionsCard onSelect={handleSampleQuestion} />
            </div>
          ) : (
            <>
              {messages.map((msg, idx) => (
                <MessageBubble
                  key={idx}
                  role={msg.role}
                  content={msg.content}
                  onSpeak={() => !isMuted && speak(msg.content)}
                  isSpeaking={isSpeaking}
                  onStopSpeak={stopSpeaking}
                />
              ))}
              {loadingIndicator && (
                <div className="flex justify-start">
                  <Card className="bg-muted px-6 py-4 rounded-3xl">
                    <div className="flex items-center gap-2">
                      <Loader2 className="h-5 w-5 animate-spin text-accent" />
                      <span className="text-sm text-muted-foreground">Analyzing your profile...</span>
                    </div>
                  </Card>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>
      </div>

      {messages.length > 0 && (
        <div className="border-t border-border bg-card sticky bottom-0 p-6">
          <div className="max-w-2xl mx-auto">
            <div className="flex gap-3">
              <Textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSendMessage(); } }}
                placeholder="Type your question or click the mic to speak..."
                className="resize-none max-h-32 bg-input border-border focus:border-accent"
              />
              <div className="flex flex-col gap-2">
                <Button size="icon" onClick={handleStartListening} className={`${isListening ? 'bg-red-500 animate-pulse' : 'bg-primary'}`}>
                  <Mic className="h-5 w-5" />
                </Button>
                <Button size="icon" onClick={handleSendMessage} disabled={!input.trim()} className="bg-accent hover:bg-emerald-600">
                  <Send className="h-5 w-5" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}