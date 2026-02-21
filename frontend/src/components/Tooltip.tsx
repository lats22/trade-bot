import { useState, useRef, useEffect } from 'react'
import './Tooltip.css'

interface TooltipProps {
  text: string
}

export function Tooltip({ text }: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false)
  const [position, setPosition] = useState({ top: 0, left: 0 })
  const containerRef = useRef<HTMLDivElement>(null)
  const contentRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsVisible(false)
      }
    }

    if (isVisible) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isVisible])

  useEffect(() => {
    if (isVisible && containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect()
      const tooltipWidth = 250
      const tooltipHeight = 100

      let top = rect.bottom + 8
      let left = rect.left + rect.width / 2 - tooltipWidth / 2

      // Keep within viewport
      if (left < 10) left = 10
      if (left + tooltipWidth > window.innerWidth - 10) {
        left = window.innerWidth - tooltipWidth - 10
      }
      if (top + tooltipHeight > window.innerHeight - 10) {
        top = rect.top - tooltipHeight - 8
      }

      setPosition({ top, left })
    }
  }, [isVisible])

  return (
    <div className="tooltip-container" ref={containerRef}>
      <button
        className="tooltip-trigger"
        onClick={() => setIsVisible(!isVisible)}
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
        aria-label="Help"
      >
        ?
      </button>
      {isVisible && (
        <div
          ref={contentRef}
          className="tooltip-content"
          style={{ top: position.top, left: position.left }}
        >
          {text}
        </div>
      )}
    </div>
  )
}
