import { useState, useRef, useEffect } from 'react'
import './Tooltip.css'

interface TooltipProps {
  text: string
}

export function Tooltip({ text }: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false)
  const tooltipRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (tooltipRef.current && !tooltipRef.current.contains(event.target as Node)) {
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

  return (
    <div className="tooltip-container" ref={tooltipRef}>
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
        <div className="tooltip-content">
          {text}
        </div>
      )}
    </div>
  )
}
