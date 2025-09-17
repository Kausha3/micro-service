import { useState, useEffect, useRef, useCallback } from 'react'
import axios from 'axios'
import './ChatWidget.css'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function ChatWidget() {
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [error, setError] = useState(null)
  // Track selected units for multiple booking
  const [selectedUnits, setSelectedUnits] = useState([])
  const messagesEndRef = useRef(null)
  const textareaRef = useRef(null)

  // Session persistence helpers
  const saveSessionToStorage = (sessionId, messages) => {
    try {
      const sessionData = {
        sessionId,
        messages,
        timestamp: Date.now(),
      }
      localStorage.setItem('chat_session', JSON.stringify(sessionData))
    } catch (error) {
      console.warn('Failed to save session to localStorage:', error)
    }
  }

  const loadSessionFromStorage = () => {
    try {
      const stored = localStorage.getItem('chat_session')
      if (!stored) {
        return null
      }

      const sessionData = JSON.parse(stored)

      // Check if session is less than 24 hours old
      const maxAge = 24 * 60 * 60 * 1000 // 24 hours in milliseconds
      if (Date.now() - sessionData.timestamp > maxAge) {
        localStorage.removeItem('chat_session')
        return null
      }

      return sessionData
    } catch (error) {
      console.warn('Failed to load session from localStorage:', error)
      localStorage.removeItem('chat_session')
      return null
    }
  }

  const clearSessionFromStorage = () => {
    try {
      localStorage.removeItem('chat_session')
    } catch (error) {
      console.warn('Failed to clear session from localStorage:', error)
    }
  }

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  // Auto-resize textarea based on content
  const autoResizeTextarea = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`
    }
  }

  // Focus textarea helper
  const focusTextarea = useCallback(() => {
    setTimeout(() => {
      if (textareaRef.current && !isLoading) {
        textareaRef.current.focus()
      }
    }, 100)
  }, [isLoading])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Auto-resize textarea when input changes
  useEffect(() => {
    autoResizeTextarea()
  }, [inputValue])

  // Focus textarea when loading ends
  useEffect(() => {
    if (!isLoading) {
      focusTextarea()
    }
  }, [isLoading, focusTextarea])

  // Initialize chat with welcome message or restore from storage
  useEffect(() => {
    const initializeChat = async () => {
      try {
        // console.log('API_BASE_URL:', API_BASE_URL)

        // Try to load existing session from storage
        const storedSession = loadSessionFromStorage()

        if (storedSession && storedSession.sessionId && storedSession.messages.length > 0) {
          // Restore existing session
          // console.log('Restoring session from localStorage:', storedSession.sessionId)
          setSessionId(storedSession.sessionId)
          setMessages(storedSession.messages)

          // Verify session is still valid on the backend
          try {
            await axios.get(`${API_BASE_URL}/sessions/${storedSession.sessionId}`)
            // console.log('Session verified on backend:', response.data)
          } catch (sessionError) {
            console.warn('Stored session not found on backend, starting fresh:', sessionError)
            // If session doesn't exist on backend, clear storage and start fresh
            clearSessionFromStorage()
            await startFreshSession()
          }
        } else {
          // Start fresh session
          await startFreshSession()
        }

        // Focus textarea after initial load
        focusTextarea()
      } catch (error) {
        console.error('Failed to initialize chat:', error)
        setError('Failed to connect to chat service. Please refresh the page.')
      }
    }

    const startFreshSession = async () => {
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        message: 'Hello',
      })

      const newSessionId = response.data.session_id
      const initialMessages = [
        {
          id: 1,
          text: response.data.reply,
          sender: 'assistant',
          timestamp: new Date().toISOString(),
        },
      ]

      setSessionId(newSessionId)
      setMessages(initialMessages)

      // Save to storage
      saveSessionToStorage(newSessionId, initialMessages)
    }

    initializeChat()
  }, [focusTextarea])

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) {
      return
    }

    const userMessage = {
      id: Date.now(),
      text: inputValue.trim(),
      sender: 'user',
      timestamp: new Date().toISOString(),
    }

    // Clear input and set loading state immediately
    setInputValue('')
    setIsLoading(true)
    setError(null)

    // Add user message immediately and get updated messages for storage
    let updatedMessagesWithUser
    setMessages(prev => {
      updatedMessagesWithUser = [...prev, userMessage]
      return updatedMessagesWithUser
    })

    try {
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        message: userMessage.text,
        session_id: sessionId,
      })

      // Add assistant response
      const assistantMessage = {
        id: Date.now() + 1,
        text: response.data.reply,
        sender: 'assistant',
        timestamp: new Date().toISOString(),
      }

      // Add assistant response and get final updated messages for storage
      let finalUpdatedMessages
      setMessages(prev => {
        finalUpdatedMessages = [...prev, assistantMessage]
        return finalUpdatedMessages
      })

      // Update session ID if provided
      const currentSessionId = response.data.session_id || sessionId
      if (response.data.session_id) {
        setSessionId(response.data.session_id)
      }

      // Save updated session to storage with the final messages
      saveSessionToStorage(currentSessionId, finalUpdatedMessages)

    } catch (error) {
      console.error('Failed to send message:', error)
      setError('Failed to send message. Please try again.')

      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'assistant',
        timestamp: new Date().toISOString(),
        isError: true,
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
      // Focus will be handled by the useEffect that watches isLoading
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const handleInputChange = (e) => {
    setInputValue(e.target.value)
  }

  // Function to handle apartment listing clicks
  const handleApartmentClick = async (unitInfo, _bedBath, _sqft, _rent) => {
    if (isLoading) {
      return
    } // Prevent clicks while loading

    // Extract unit ID from the unit info (e.g., "• Unit B301" -> "B301")
    const unitIdMatch = unitInfo.match(/Unit ([A-Z0-9]+)/)
    if (!unitIdMatch) {
      return
    }

    const unitId = unitIdMatch[1]

    // Check if unit is already selected
    const isAlreadySelected = selectedUnits.includes(unitId)

    let bookingMessage
    if (isAlreadySelected) {
      // Remove from selection
      setSelectedUnits(prev => prev.filter(id => id !== unitId))
      bookingMessage = `Remove unit ${unitId} from my selections`
    } else {
      // Add to selection
      setSelectedUnits(prev => [...prev, unitId])
      bookingMessage = `Add unit ${unitId} to my selections`
    }

    // Create user message object
    const userMessage = {
      id: Date.now(),
      text: bookingMessage,
      sender: 'user',
      timestamp: new Date().toISOString(),
    }

    // Set loading state immediately
    setIsLoading(true)
    setError(null)

    // Add user message immediately and get updated messages for storage
    let updatedMessagesWithUser
    setMessages(prev => {
      updatedMessagesWithUser = [...prev, userMessage]
      return updatedMessagesWithUser
    })

    try {
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        message: bookingMessage,
        session_id: sessionId,
      })

      // Add assistant response
      const assistantMessage = {
        id: Date.now() + 1,
        text: response.data.reply,
        sender: 'assistant',
        timestamp: new Date().toISOString(),
      }

      // Add assistant response and get final updated messages for storage
      let finalUpdatedMessages
      setMessages(prev => {
        finalUpdatedMessages = [...prev, assistantMessage]
        return finalUpdatedMessages
      })

      // Update session ID if provided
      const currentSessionId = response.data.session_id || sessionId
      if (response.data.session_id) {
        setSessionId(response.data.session_id)
      }

      // Save updated session to storage with the final messages
      saveSessionToStorage(currentSessionId, finalUpdatedMessages)

    } catch (error) {
      console.error('Failed to send apartment selection:', error)
      setError('Failed to select apartment. Please try again.')

      // Revert selection change on error
      if (isAlreadySelected) {
        setSelectedUnits(prev => [...prev, unitId])
      } else {
        setSelectedUnits(prev => prev.filter(id => id !== unitId))
      }

      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, I encountered an error selecting that apartment. Please try again.',
        sender: 'assistant',
        timestamp: new Date().toISOString(),
        isError: true,
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const startNewChat = async () => {
    try {
      setIsLoading(true)
      setError(null)

      // Clear storage and state
      clearSessionFromStorage()
      setMessages([])
      setSessionId(null)
      setInputValue('')

      // Start fresh session
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        message: 'Hello',
      })

      const newSessionId = response.data.session_id
      const initialMessages = [
        {
          id: 1,
          text: response.data.reply,
          sender: 'assistant',
          timestamp: new Date().toISOString(),
        },
      ]

      setSessionId(newSessionId)
      setMessages(initialMessages)

      // Save to storage
      saveSessionToStorage(newSessionId, initialMessages)

      // Focus textarea
      focusTextarea()
    } catch (error) {
      console.error('Failed to start new chat:', error)
      setError('Failed to start new chat. Please refresh the page.')
    } finally {
      setIsLoading(false)
    }
  }

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  // Function to detect and format apartment listings
  const formatMessageText = (text) => {
    // Check if the message contains apartment listings with the new format
    const apartmentListingRegex = /• Unit [A-Z0-9]+ \|/

    if (apartmentListingRegex.test(text)) {
      // Split the text into parts and format apartment listings
      const parts = text.split('\n')
      return parts.map((part, index) => {
        // Check for apartment listing pattern
        if (part.match(/• Unit [A-Z0-9]+ \|/)) {
          // This is an apartment listing - format it specially
          const listingParts = part.split(' | ')
          if (listingParts.length >= 4) {
            const unitInfo = listingParts[0] // "• Unit A101"
            const bedBath = listingParts[1] // "1 bed/1 bath"
            const sqft = listingParts[2] // "650 sq ft"
            const rent = listingParts[3] // "$1,800/month"

            // Extract unit ID to check if it's selected
            const unitIdMatch = unitInfo.match(/Unit ([A-Z0-9]+)/)
            const unitId = unitIdMatch ? unitIdMatch[1] : null
            const isSelected = unitId && selectedUnits.includes(unitId)

            return (
              <div
                key={unitId || `apartment-${index}`}
                className={`apartment-listing clickable ${isLoading ? 'loading' : ''} ${isSelected ? 'selected' : ''}`}
                onClick={() => !isLoading && handleApartmentClick(unitInfo, bedBath, sqft, rent)}
                onKeyDown={(e) => {
                  if ((e.key === 'Enter' || e.key === ' ') && !isLoading) {
                    e.preventDefault()
                    handleApartmentClick(unitInfo, bedBath, sqft, rent)
                  }
                }}
                role="button"
                tabIndex={0}
                title={isLoading ? 'Processing...' : isSelected ? 'Click to remove from selections' : 'Click to add to selections'}
              >
                <span className="unit-id">{unitInfo}</span>
                <span className="bed-bath">{bedBath}</span>
                <span className="sqft">{sqft}</span>
                <span className="rent">{rent}</span>
                <span className="click-hint">
                  {isLoading ? '⏳ Processing...' :
                    isSelected ? '✅ Selected' :
                      '📋 Click to select'}
                </span>
              </div>
            )
          }
        } else if (part.match(/• [A-Za-z0-9\-\s]+ Units \|/)) {
          // Check for category headers like "• Studio Units | ..."
          // This is a unit category summary - format it specially
          const listingParts = part.split(' | ')
          if (listingParts.length >= 4) {
            const categoryInfo = listingParts[0] // "• Studio Units"
            const bedBath = listingParts[1] // "0 bed/1 bath"
            const sqft = listingParts[2] // "450-500 sq ft"
            const rent = listingParts[3] // "$1,500-1,600/month"

            return (
              <div key={categoryInfo || `category-${index}`} className="apartment-listing category-listing">
                <span className="unit-id">{categoryInfo}</span>
                <span className="bed-bath">{bedBath}</span>
                <span className="sqft">{sqft}</span>
                <span className="rent">{rent}</span>
              </div>
            )
          }
        }
        // Regular text line
        return part && <div key={`text-${part.slice(0, 30).replace(/\s+/g, '-')}`}>{part}</div>
      })
    }

    // Regular message - return as is
    return text
  }

  return (
    <div className="chat-widget">
      <div className="chat-header">
        <h3>Chat Assistant</h3>
        <div className="header-controls">
          {selectedUnits.length > 0 && (
            <div className="selected-units-indicator" title={`Selected units: ${selectedUnits.join(', ')}`}>
              📋 {selectedUnits.length} selected
            </div>
          )}
          <button
            onClick={startNewChat}
            disabled={isLoading}
            className="new-chat-button"
            title="Start a new conversation"
          >
            🔄 New Chat
          </button>
        </div>
      </div>
      <div className="chat-messages">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`message ${message.sender} ${message.isError ? 'error' : ''}`}
          >
            <div className="message-content">
              <div className="message-text">{formatMessageText(message.text)}</div>
              <div className="message-time">{formatTime(message.timestamp)}</div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message assistant">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <div className="message-text typing-text">Assistant is typing...</div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className="error-banner">
          {error}
          <button onClick={() => setError(null)} className="error-close">×</button>
        </div>
      )}

      <div className="chat-input-container">
        <div className="chat-input">
          <textarea
            ref={textareaRef}
            value={inputValue}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder="Type your message..."
            disabled={isLoading}
            rows={1}
            aria-label="Type your message"
            style={{ resize: 'none', overflow: 'hidden' }}
          />
          <button
            onClick={sendMessage}
            disabled={!inputValue.trim() || isLoading}
            className="send-button"
            aria-label="Send message"
            type="button"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path
                d="M22 2L11 13M22 2L15 22L11 13M22 2L2 9L11 13"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
        </div>

        <div className="chat-hints">
          <span>
            💡 Try: &ldquo;I&apos;m looking for a 2-bedroom apartment&rdquo; or click units to select
            multiple apartments
          </span>
        </div>
      </div>
    </div>
  )
}

export default ChatWidget
