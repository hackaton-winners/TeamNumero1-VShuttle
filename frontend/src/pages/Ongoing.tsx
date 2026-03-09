import { CheckCircle2 } from "lucide-react"

import { Slider } from "@/components/ui/slider"

type OngoingProps = {
  confidence?: number
}

export function Ongoing({ confidence = 70 }: OngoingProps) {
  return (
    <div className="h-full w-full p-6">
      <div className="mx-auto flex h-full w-full flex-col gap-12">
        <div className="relative w-full pt-2">
          <Slider
            aria-label="Livello di confidence"
            className="w-full"
            trackClassName="h-16 rounded-md"
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

        <div className="flex flex-1 flex-col items-center justify-center gap-3 text-center">
          <CheckCircle2 className="size-48 text-green-500" aria-hidden="true" />
          <p className="text-6xl font-semibold">PUOI PROSEGUIRE</p>
        </div>
      </div>
    </div>
  )
}
