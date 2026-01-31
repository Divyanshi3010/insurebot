'use client';

import { useState, useCallback } from 'react'
import { toast } from 'sonner'

export interface Message {
  role: 'user' | 'model'
  content: string
}

export interface Recommendation {
  company: string
  product_name: string
  premium_estimate: number
  csr: number
  score: number
  usp: string
}

export function useChatBot() {
  const [messages, setMessages] = useState<Message[]>([])
  const [recommendations, setRecommendations] = useState<Recommendation[] | null>(null)
  const [loadingIndicator, setLoadingIndicator] = useState(false)

  const sendMessage = useCallback(async (userMessage: string) => {
    if (!userMessage.trim()) return

    const newUserMessage: Message = { role: 'user', content: userMessage }
    setMessages((prev) => [...prev, newUserMessage])
    setLoadingIndicator(true)

    try {
      const messagesForAPI = [
        ...messages,
        newUserMessage,
      ]

      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: messagesForAPI.map((msg) => ({
            role: msg.role,
            content: msg.content,
          })),
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to send message')
      }

      const data = await response.json()
      const aiResponse = data.response || ''

      const newAiMessage: Message = {
        role: 'model',
        content: aiResponse,
      }
      setMessages((prev) => [...prev, newAiMessage])

      if (data.recommendations) {
        setRecommendations(data.recommendations)
        toast.success('Insurance plans personalized for you!')
      }
    } catch (error) {
      console.error('Error sending message:', error)
      toast.error('Failed to send message. Please try again.')
      const mockResponse: Message = {
        role: 'model',
        content: 'I apologize for the technical difficulty. Please ensure the backend server is accessible.',
      }
      setMessages((prev) => [...prev, mockResponse])
    } finally {
      setLoadingIndicator(false)
    }
  }, [messages])

  return {
    messages,
    sendMessage,
    recommendations,
    loadingIndicator,
  }
}