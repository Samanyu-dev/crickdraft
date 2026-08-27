import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

function useCountUp(target: number, duration = 900) {
  const [display, setDisplay] = useState(0)
  useEffect(() => {
    let raf: number
    const start = performance.now()
    const from = display
    function tick(now: number) {
      const t = Math.min(1, (now - start) / duration)
      const eased = 1 - Math.pow(1 - t, 3)
      setDisplay(Math.round(from + (target - from) * eased))
      if (t < 1) raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [target])
  return display
}

function FlipDigit({ char }: { char: string }) {
  return (
    <span className="flip-digit">
      <AnimatePresence mode="popLayout" initial={false}>
        <motion.span
          key={char}
          initial={{ y: 14, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: -14, opacity: 0 }}
          transition={{ duration: 0.18 }}
        >
          {char}
        </motion.span>
      </AnimatePresence>
    </span>
  )
}

export default function FlipScore({ value }: { value: number }) {
  const display = useCountUp(value)
  const chars = String(display).split('')
  return (
    <div className="flip-score">
      {chars.map((c, i) => (
        <FlipDigit key={i} char={c} />
      ))}
    </div>
  )
}
