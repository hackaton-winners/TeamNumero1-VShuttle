import { CircleX } from "lucide-react"

import { Slider } from "@/components/ui/slider"

type StopProps = {
  message?: string
  subMessage?: string
  confidence?: number
}

export function Stop({
  message = "STOP",
  subMessage = "Operazione interrotta",
  confidence = 0,
}: StopProps) {
  return (
    <div className="h-full w-full p-6">
      <div className="mx-auto flex h-full w-full flex-col">
        <div className="relative w-full pt-2">
          <Slider
            aria-label="Livello di confidence"
            className="w-full"
            trackClassName="h-16 rounded-md"
            rangeClassName="bg-destructive"
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

        <div className="flex flex-1 flex-col items-center justify-center gap-12 text-center">
          <CircleX className="size-48 text-destructive" aria-hidden="true" />
          <div className="space-y-4">
            <p className="text-6xl leading-tight font-semibold">{message}</p>
            <p className="text-3xl leading-snug font-medium text-foreground/85">
              {subMessage}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
