import { useEffect, useState } from "react"
import { TriangleAlert } from "lucide-react"

import { Slider } from "@/components/ui/slider"
import { Button } from "@/components/ui/button"

type WarningProps = {
  message?: string
  subMessage?: string
  countdownFrom?: number
  confidence?: number
  onOverride?: () => void
  onStop?: () => void
}

export function Warning({
  message = "STOP",
  subMessage = "Operazione interrotta",
  countdownFrom = 10,
  confidence = 0,
  onOverride,
  onStop,
}: WarningProps) {
  const safeStart = Math.max(0, Math.floor(countdownFrom))
  const totalMs = safeStart * 1000
  const [remainingMs, setRemainingMs] = useState(totalMs)

  useEffect(() => {
    setRemainingMs(totalMs)
  }, [totalMs])

  useEffect(() => {
    if (totalMs <= 0) {
      return
    }

    const startTime = performance.now()
    const endTime = startTime + totalMs
    let rafId = 0

    const tick = (now: number) => {
      const nextRemainingMs = Math.max(0, endTime - now)
      setRemainingMs(nextRemainingMs)

      if (nextRemainingMs > 0) {
        rafId = window.requestAnimationFrame(tick)
      }
    }

    rafId = window.requestAnimationFrame(tick)

    return () => window.cancelAnimationFrame(rafId)
  }, [totalMs])

  const secondsLeft = Math.ceil(remainingMs / 1000)
  const progress = totalMs === 0 ? 0 : (remainingMs / totalMs) * 100

  const roundedProgress = Number(progress.toFixed(3))

  return (
    <div className="h-full w-full p-6">
      <div className="mx-auto flex h-full w-full flex-col">
        <div className="relative w-full pt-2">
          <Slider
            aria-label="Livello di confidence"
            className="w-full"
            trackClassName="h-16 rounded-md"
            rangeClassName="bg-warning"
            max={100}
            step={1}
            value={[confidence]}
            disabled
            showThumb={false}
          />
          <p className="pointer-events-none absolute inset-0 flex items-center justify-center text-2xl font-bold text-foreground">
            Confidence: {confidence}%
          </p>
        </div>

        <div className="relative mt-4 w-full">
          <Slider
            aria-label="Tempo rimanente"
            className="w-full"
            trackClassName="h-10 rounded-md"
            rangeClassName="bg-warning/60"
            max={100}
            step={0.001}
            value={[roundedProgress]}
            disabled
            showThumb={false}
          />
          <p className="pointer-events-none absolute inset-0 flex items-center justify-center text-lg font-bold text-foreground">
            {secondsLeft}s rimanenti
          </p>
        </div>

        <div className="flex flex-1 flex-col items-center justify-center gap-12 text-center">
          <TriangleAlert className="size-48 text-warning" aria-hidden="true" />
          <div className="space-y-4">
            <p className="text-6xl leading-tight font-semibold">{message}</p>
            <p className="text-3xl leading-snug font-medium text-foreground/85">
              {subMessage}
            </p>

            <div className="flex justify-center gap-2 pt-8">
              <Button size={"lg"} className="bg-success" onClick={onOverride}>
                Prosegui
              </Button>
              <Button size={"lg"} className="bg-destructive" onClick={onStop}>
                Arresta
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
