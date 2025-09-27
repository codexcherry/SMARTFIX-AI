"use client"

import { useState, useEffect, useRef } from "react"
import {
  Box,
  Typography,
  TextField,
  Button,
  Avatar,
  CircularProgress,
  IconButton,
  Tooltip,
  Fade,
  Alert,
} from "@mui/material"
import {
  Send as SendIcon,
  SmartToy as AssistantIcon,
  KeyboardArrowDown as ScrollDownIcon,
  Wifi,
  WifiOff,
  CloudOff,
  Refresh as RefreshIcon,
} from "@mui/icons-material"
import { querySmartAssistant, getSmartAssistantStatus } from "../services/smartAssistantApi"

const SmartAssistantChat = () => {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [assistantStatus, setAssistantStatus] = useState(null)
  const [error, setError] = useState(null)
  const [showScrollButton, setShowScrollButton] = useState(false)
  const [networkStatus, setNetworkStatus] = useState("checking")
  const [conversationHistory, setConversationHistory] = useState([])

  const messagesEndRef = useRef(null)
  const chatContainerRef = useRef(null)

  // Load assistant status and conversation history
  useEffect(() => {
    loadAssistantStatus()
    const savedHistory = localStorage.getItem("smartAssistantHistory")
    if (savedHistory) {
      try {
        const parsedHistory = JSON.parse(savedHistory)
        setMessages(parsedHistory)
      } catch (error) {
        console.error("Error loading conversation history:", error)
      }
    }
  }, [])

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Save conversation history
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem("smartAssistantHistory", JSON.stringify(messages))
    }
  }, [messages])

  // Check scroll position for scroll button
  useEffect(() => {
    const handleScroll = () => {
      if (chatContainerRef.current) {
        const { scrollTop, scrollHeight, clientHeight } = chatContainerRef.current
        setShowScrollButton(scrollHeight - scrollTop - clientHeight > 100)
      }
    }

    const container = chatContainerRef.current
    if (container) {
      container.addEventListener("scroll", handleScroll)
      return () => container.removeEventListener("scroll", handleScroll)
    }
  }, [])

  const loadAssistantStatus = async () => {
    try {
      const status = await getSmartAssistantStatus()
      setAssistantStatus(status)
      setNetworkStatus(status.network_status || "unknown")
    } catch (error) {
      console.error("Error loading assistant status:", error)
      setNetworkStatus("offline")
    }
  }

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" })
    }
  }

  const clearConversation = () => {
    setMessages([])
    setConversationHistory([])
    localStorage.removeItem("smartAssistantHistory")
  }

  const handleSendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage = {
      id: Date.now(),
      type: "user",
      content: input.trim(),
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setLoading(true)
    setError(null)

    try {
      const response = await querySmartAssistant(input.trim(), true)
      
      // Debug logging
      console.log("Smart Assistant Response:", response)
      console.log("Response keys:", Object.keys(response))
      console.log("Response type:", typeof response)

      // Handle different response formats
      let formattedResponse = ""
      let solution = {}
      let confidence = 0
      let source = "unknown"
      let networkStatus = "unknown"

      if (response.success === false) {
        // Handle error responses
        formattedResponse = response.response || response.error || "I apologize, but I couldn't process your request."
        solution = {}
        confidence = 0
        source = "error"
        networkStatus = "offline"
      } else {
        // Handle successful responses
        console.log("Processing successful response...")
        
        // First, try to find any direct text response
        const textFields = ['response', 'answer', 'message', 'text', 'content', 'result', 'output']
        let foundText = null
        for (const field of textFields) {
          if (response[field] && typeof response[field] === 'string' && response[field].trim().length > 10) {
            foundText = response[field]
            console.log(`Found text in field '${field}':`, foundText)
            break
          }
        }
        
        if (foundText) {
          formattedResponse = foundText
          solution = response.solution || {}
        } else if (response.solution && typeof response.solution === 'object') {
          // Structured solution object
          console.log("Processing structured solution...")
          formattedResponse = formatResponse(response.solution)
          solution = response.solution
        } else {
          // Try to format the entire response as a fallback
          console.log("Using fallback formatting for entire response...")
          formattedResponse = formatResponse(response)
          solution = response
        }
        
        confidence = Math.round((response.confidence_score || 0) * 100) / 100
        source = response.source || "unknown"
        networkStatus = response.network_status || "unknown"
      }
      
      // Debug logging for formatted response
      console.log("Formatted Response:", formattedResponse)
      
      // If the response is still empty or too short, try to extract more information
      if (!formattedResponse || formattedResponse.length < 10) {
        console.log("Response too short, trying to extract more info from:", response)
        
        // Try to extract any meaningful text from the entire response object
        const extractTextFromObject = (obj, depth = 0) => {
          if (depth > 3) return "" // Prevent infinite recursion
          
          let text = ""
          for (const [key, value] of Object.entries(obj)) {
            if (typeof value === 'string' && value.trim().length > 10) {
              text += value + " "
            } else if (typeof value === 'object' && value !== null) {
              text += extractTextFromObject(value, depth + 1)
            }
          }
          return text.trim()
        }
        
        const extractedText = extractTextFromObject(response)
        if (extractedText) {
          formattedResponse = extractedText
        }
      }

      const assistantMessage = {
        id: Date.now() + 1,
        type: "assistant",
        content: formattedResponse,
        solution: solution,
        confidence: confidence,
        source: source,
        networkStatus: networkStatus,
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, assistantMessage])
      setConversationHistory((prev) => [...prev, userMessage, assistantMessage])

      if (networkStatus && networkStatus !== networkStatus) {
        setNetworkStatus(networkStatus)
      }
    } catch (error) {
      console.error("Error sending message:", error)
      setError("Failed to get response from assistant. Please try again.")

      const errorMessage = {
        id: Date.now() + 1,
        type: "error",
        content: "I apologize, but I encountered an error while processing your request. Please try again.",
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault()
      handleSendMessage()
    }
  }

  const formatResponse = (solution) => {
    // Handle different solution formats
    if (typeof solution === 'string') {
      return solution
    }

    if (!solution || typeof solution !== 'object') {
      return "I've analyzed your request and provided a response."
    }

    // Debug log the solution object
    console.log("Solution object:", solution)

    // If we have a direct response, use it
    if (solution?.response) {
      return solution.response
    }

    // If we have a direct answer, use it
    if (solution?.answer) {
      return solution.answer
    }

    // Try to extract the main issue/description
    const issue = solution?.issue || 
                  solution?.problem || 
                  solution?.description || 
                  solution?.summary ||
                  solution?.title ||
                  "Unknown issue"
    
    const possibleCauses = solution?.possible_causes || 
                          solution?.causes || 
                          solution?.root_causes ||
                          []
    
    const steps = solution?.recommended_steps || 
                 solution?.steps || 
                 solution?.solution_steps ||
                 solution?.actions ||
                 []

    let response = `I've analyzed your issue: ${issue}. `

    if (possibleCauses.length > 0) {
      const validCauses = possibleCauses.filter(
        (cause) =>
          cause &&
          typeof cause === 'string' &&
          !cause.includes("Error:") &&
          !cause.includes("Unable to determine") &&
          !cause.includes("404") &&
          !cause.includes("models/gemini") &&
          !cause.includes("None") &&
          !cause.includes("null") &&
          cause.trim().length > 0
      )

      if (validCauses.length > 0) {
        if (validCauses.length === 1) {
          response += `The likely cause is ${validCauses[0]}. `
        } else {
          response += `Possible causes include ${validCauses[0]}`
          if (validCauses.length > 1) {
            response += ` or ${validCauses[1]}`
          }
          response += ". "
        }
      }
    }

    if (steps.length > 0) {
      response += "Here's what you can do: "
      steps.slice(0, 3).forEach((step, i) => {
        let stepDesc = ""
        if (typeof step === 'string') {
          stepDesc = step
        } else if (step && typeof step === 'object') {
          stepDesc = step.description || step.step || step.text || step.action || ""
        }
        
        if (stepDesc.trim()) {
          response += `${i + 1}) ${stepDesc.trim()} `
        }
      })
    }

    // If no structured data, try to extract any meaningful text from the response
    if (response === `I've analyzed your issue: ${issue}. `) {
      // Look for any text content in the response
      const textFields = ['content', 'text', 'message', 'details', 'explanation', 'description', 'summary']
      for (const field of textFields) {
        if (solution[field] && typeof solution[field] === 'string' && solution[field].trim()) {
          return solution[field]
        }
      }
      
      // Try to extract any meaningful text from the entire object
      const extractAllText = (obj, depth = 0) => {
        if (depth > 2) return ""
        
        let allText = ""
        for (const [key, value] of Object.entries(obj)) {
          if (typeof value === 'string' && value.trim().length > 20) {
            allText += value + " "
          } else if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
            allText += extractAllText(value, depth + 1)
          } else if (Array.isArray(value)) {
            value.forEach(item => {
              if (typeof item === 'string' && item.trim().length > 20) {
                allText += item + " "
              }
            })
          }
        }
        return allText.trim()
      }
      
      const extractedText = extractAllText(solution)
      if (extractedText) {
        return extractedText
      }
      
      // If still no content, return a helpful message with more details
      return `I found a solution to your issue in my offline knowledge base. The issue appears to be: ${issue}. Please check the console logs for more detailed information about the response structure.`
    }

    return response.trim()
  }

  const getStatusIcon = () => {
    switch (networkStatus) {
      case "online":
        return <Wifi sx={{ fontSize: 16, color: "#10a37f" }} />
      case "offline":
        return <WifiOff sx={{ fontSize: 16, color: "#ef4444" }} />
      case "checking":
        return <CircularProgress size={16} sx={{ color: "#6b7280" }} />
      default:
        return <CloudOff sx={{ fontSize: 16, color: "#f59e0b" }} />
    }
  }

  const renderMessage = (message) => {
    const isUser = message.type === "user"
    const isError = message.type === "error"

    return (
      <Box
        key={message.id}
        sx={{
          display: "flex",
          justifyContent: isUser ? "flex-end" : "flex-start",
          width: "100%",
          mb: 1,
          px: 2,
        }}
      >
        <Box
          sx={{
            maxWidth: "70%",
            display: "flex",
            alignItems: "flex-end",
            gap: 1,
            flexDirection: isUser ? "row-reverse" : "row",
          }}
        >
          <Avatar
            sx={{
              width: 28,
              height: 28,
              bgcolor: isUser ? "#007bff" : isError ? "#ef4444" : "#10a37f",
              fontSize: "12px",
              fontWeight: "bold",
              flexShrink: 0,
              mb: 0.5,
            }}
          >
            {isUser ? "U" : isError ? "!" : "AI"}
          </Avatar>

          <Box
            sx={{
              backgroundColor: isUser ? "#007bff" : "#2d2d2d",
              color: isUser ? "#ffffff" : "#ffffff",
              borderRadius: isUser ? "18px 18px 4px 18px" : "18px 18px 18px 4px",
              px: 3,
              py: 2,
              maxWidth: "100%",
              wordBreak: "break-word",
              boxShadow: "0 1px 2px rgba(0, 0, 0, 0.1)",
            }}
          >
            <Typography
              variant="body1"
              sx={{
                fontSize: "14px",
                lineHeight: 1.4,
                whiteSpace: "pre-wrap",
                margin: 0,
              }}
            >
              {message.content}
            </Typography>

            <Typography
              variant="caption"
              sx={{
                fontSize: "11px",
                opacity: 0.7,
                display: "block",
                textAlign: isUser ? "right" : "left",
                mt: 0.5,
              }}
            >
              {new Date(message.timestamp).toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
              })}
            </Typography>
          </Box>
        </Box>
      </Box>
    )
  }

  return (
    <Box
      sx={{
        height: "100%",
        display: "flex",
        flexDirection: "column",
        backgroundColor: "#000000",
        position: "relative",
      }}
    >
      {/* Header */}
      <Box
        sx={{
          p: 2,
          borderBottom: "1px solid #333333",
          backgroundColor: "#000000",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          position: "sticky",
          top: 0,
          zIndex: 10,
        }}
      >
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          <Typography
            variant="h6"
            sx={{
              color: "#ffffff",
              fontWeight: 600,
              fontSize: "18px",
            }}
          >
            Smart Assistant
          </Typography>
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            {getStatusIcon()}
            <Typography
              variant="caption"
              sx={{
                color: "#cccccc",
                fontSize: "12px",
                textTransform: "uppercase",
                letterSpacing: "0.5px",
              }}
            >
              {networkStatus}
            </Typography>
          </Box>
        </Box>

        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          {messages.length > 0 && (
            <Tooltip title="Clear conversation">
              <IconButton
                size="small"
                onClick={clearConversation}
                sx={{
                  color: "#cccccc",
                  "&:hover": {
                    backgroundColor: "#333333",
                    color: "#ffffff",
                  },
                }}
              >
                <RefreshIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          )}
        </Box>
      </Box>

      {/* Messages area */}
      <Box
        ref={chatContainerRef}
        sx={{
          flex: 1,
          overflowY: "auto",
          overflowX: "hidden",
          backgroundColor: "#000000",
          display: "flex",
          flexDirection: "column",
          justifyContent: messages.length === 0 ? "center" : "flex-end",
          "&::-webkit-scrollbar": {
            width: "6px",
          },
          "&::-webkit-scrollbar-track": {
            background: "transparent",
          },
          "&::-webkit-scrollbar-thumb": {
            background: "#333333",
            borderRadius: "3px",
            "&:hover": {
              background: "#555555",
            },
          },
        }}
      >
        {messages.length === 0 ? (
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              p: 4,
              textAlign: "center",
            }}
          >
            <Box
              sx={{
                width: 64,
                height: 64,
                borderRadius: "50%",
                backgroundColor: "#333333",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                mb: 3,
              }}
            >
              <AssistantIcon sx={{ fontSize: 32, color: "#ffffff" }} />
            </Box>
            <Typography
              variant="h5"
              sx={{
                color: "#ffffff",
                fontWeight: 600,
                mb: 1,
              }}
            >
              How can I help you today?
            </Typography>
            <Typography
              variant="body1"
              sx={{
                color: "#cccccc",
                maxWidth: "400px",
              }}
            >
              Ask me anything about your technical issues and I'll provide intelligent solutions.
            </Typography>
          </Box>
        ) : (
          <Box sx={{ py: 2 }}>{messages.map(renderMessage)}</Box>
        )}

        {loading && (
          <Box
            sx={{
              display: "flex",
              justifyContent: "flex-start",
              width: "100%",
              mb: 1,
              px: 2,
            }}
          >
            <Box
              sx={{
                maxWidth: "70%",
                display: "flex",
                alignItems: "flex-end",
                gap: 1,
              }}
            >
              <Avatar
                sx={{
                  width: 28,
                  height: 28,
                  bgcolor: "#10a37f",
                  fontSize: "12px",
                  fontWeight: "bold",
                  flexShrink: 0,
                  mb: 0.5,
                }}
              >
                AI
              </Avatar>
              <Box
                sx={{
                  backgroundColor: "#2d2d2d",
                  borderRadius: "18px 18px 18px 4px",
                  px: 3,
                  py: 2,
                  display: "flex",
                  alignItems: "center",
                  gap: 1,
                }}
              >
                <CircularProgress size={16} sx={{ color: "#ffffff" }} />
                <Typography variant="body2" sx={{ color: "#ffffff", fontSize: "14px" }}>
                  Thinking...
                </Typography>
              </Box>
            </Box>
          </Box>
        )}

        <div ref={messagesEndRef} />
      </Box>

      {/* Input area */}
      <Box
        sx={{
          p: 3,
          backgroundColor: "#000000",
          borderTop: "1px solid #1e3a8a",
          position: "sticky",
          bottom: 0,
          zIndex: 10,
        }}
      >
        <Box
          sx={{
            display: "flex",
            gap: 2,
            alignItems: "flex-end",
            maxWidth: "768px",
            margin: "0 auto",
          }}
        >
          <TextField
            fullWidth
            multiline
            maxRows={4}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Message Smart Assistant..."
            disabled={loading}
            variant="outlined"
            sx={{
              "& .MuiOutlinedInput-root": {
                backgroundColor: "#1a1a1a",
                borderRadius: "24px",
                color: "#ffffff",
                "& fieldset": {
                  borderColor: "#3b82f6",
                },
                "&:hover fieldset": {
                  borderColor: "#60a5fa",
                },
                "&.Mui-focused fieldset": {
                  borderColor: "#2563eb",
                  borderWidth: "2px",
                  boxShadow: "0 0 0 3px rgba(37, 99, 235, 0.1)",
                },
              },
              "& .MuiInputBase-input": {
                padding: "12px 16px",
                fontSize: "16px",
                color: "#ffffff",
                "&::placeholder": {
                  color: "#93c5fd",
                  opacity: 1,
                },
              },
            }}
          />
          <Button
            variant="contained"
            onClick={handleSendMessage}
            disabled={!input.trim() || loading}
            sx={{
              minWidth: "48px",
              height: "48px",
              borderRadius: "50%",
              background: "linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)",
              "&:hover": {
                background: "linear-gradient(135deg, #2563eb 0%, #1e40af 100%)",
                boxShadow: "0 0 20px rgba(59, 130, 246, 0.5)",
              },
              "&:disabled": {
                backgroundColor: "#374151",
                color: "#6b7280",
              },
              boxShadow: "0 4px 12px rgba(59, 130, 246, 0.3)",
            }}
          >
            <SendIcon />
          </Button>
        </Box>

        {error && (
          <Alert
            severity="error"
            sx={{
              mt: 2,
              maxWidth: "768px",
              margin: "16px auto 0 auto",
              borderRadius: "8px",
              backgroundColor: "#1f2937",
              color: "#ffffff",
              "& .MuiAlert-icon": {
                color: "#ef4444",
              },
            }}
            onClose={() => setError(null)}
          >
            {error}
          </Alert>
        )}
      </Box>

      {/* Scroll to bottom button */}
      <Fade in={showScrollButton}>
        <IconButton
          onClick={scrollToBottom}
          sx={{
            position: "absolute",
            bottom: 100,
            right: 24,
            backgroundColor: "#1e3a8a",
            color: "#60a5fa",
            border: "1px solid #3b82f6",
            boxShadow: "0 4px 12px rgba(59, 130, 246, 0.2)",
            "&:hover": {
              backgroundColor: "#1e40af",
              color: "#93c5fd",
              boxShadow: "0 6px 16px rgba(59, 130, 246, 0.3)",
            },
          }}
        >
          <ScrollDownIcon />
        </IconButton>
      </Fade>
    </Box>
  )
}

export default SmartAssistantChat