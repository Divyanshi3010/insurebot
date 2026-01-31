'use client'

import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { ArrowRight, Shield, Brain, BarChart3 } from 'lucide-react'
import Image from 'next/image'

export default function Home() {
  const router = useRouter()

  return (
    <div className="flex flex-col min-h-screen">
      {/* Header */}
      <header className="sticky top-0 z-40 border-b border-border bg-background/95 backdrop-blur">
        <div className="flex h-20 items-center justify-between px-6">
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
          <Button onClick={() => router.push('/chat')} className="bg-accent hover:bg-black text-white">
            Start Chat
          </Button>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1 flex flex-col items-center justify-center px-6 py-20">
        <div className="max-w-3xl mx-auto text-center space-y-8">
          <div className="space-y-6">
            <div className="flex items-center justify-center">
              <span className="text-6xl md:text-7xl font-bold bg-gradient-to-r from-sky-500 via-blue-600 to-rose-500 bg-clip-text text-transparent">InsureBot</span>
            </div>
            <p className="text-xl text-muted-foreground leading-relaxed">
              Get personalized term life insurance recommendations from our expert AI advisor. Answer a few questions about your financial profile and receive tailored plan suggestions in minutes.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center pt-8">
            <Button
              onClick={() => router.push('/chat')}
              size="lg"
              className="bg-primary hover:bg-accent text-white"
            >
              Talk to InsureBot <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </div>

          <div className="grid md:grid-cols-3 gap-6 pt-12">
            <div className="flex flex-col items-start space-y-3 p-6 rounded-lg border border-border bg-card hover:shadow-lg transition-shadow">
              <div className="h-12 w-12 rounded-lg bg-accent/10 flex items-center justify-center">
                <Brain className="h-6 w-6 text-accent" />
              </div>
              <h3 className="font-semibold text-lg text-primary dark:text-white">AI Expert Advisor</h3>
              <p className="text-sm text-muted-foreground">
                Conversational AI that understands insurance needs and guides you naturally
              </p>
            </div>

            <div className="flex flex-col items-start space-y-3 p-6 rounded-lg border border-border bg-card hover:shadow-lg transition-shadow">
              <div className="h-12 w-12 rounded-lg bg-accent/10 flex items-center justify-center">
                <BarChart3 className="h-6 w-6 text-accent" />
              </div>
              <h3 className="font-semibold text-lg text-primary dark:text-white">Data-Driven Plans</h3>
              <p className="text-sm text-muted-foreground">
                Recommendations based on your age, income, liabilities, and lifestyle
              </p>
            </div>

            <div className="flex flex-col items-start space-y-3 p-6 rounded-lg border border-border bg-card hover:shadow-lg transition-shadow">
              <div className="h-12 w-12 rounded-lg bg-accent/10 flex items-center justify-center">
                <Shield className="h-6 w-6 text-accent" />
              </div>
              <h3 className="font-semibold text-lg text-primary dark:text-white">Trusted Insurers</h3>
              <p className="text-sm text-muted-foreground">
                Compare plans from India's top insurance companies with verified CSR data
              </p>
            </div>
          </div>
        </div>
      </main>

      <footer className="border-t border-border bg-background py-8">
        <div className="flex flex-col md:flex-row items-center justify-between px-6 max-w-7xl mx-auto">
          <p className="text-sm text-muted-foreground">
            © 2025 Share India Insurance & Brokers. All rights reserved.
          </p>
          <p className="text-xs text-muted-foreground mt-4 md:mt-0">
            InsureBot is powered by Gemini AI and provides indicative recommendations
          </p>
        </div>
      </footer>
    </div>
  )
}