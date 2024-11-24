export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  id: string
  error?: string
  componentType?: string
  componentProps?: Record<string, any>
  submitResponse?: Record<string, any>
  createdAt: number
}
