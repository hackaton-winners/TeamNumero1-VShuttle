import { CheckCircle2 } from "lucide-react"

import { Slider } from "@/components/ui/slider"

type OngoingProps = {
  confidence?: number
}

export function Ongoing({ confidence = 70 }: OngoingProps) {
  return (
    <div className="h-full w-full p-6">
      <div className="mx-auto flex h-full w-full flex-col gap-12">
        <div className="pt-2">
          {/* <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Livello di confidence</span>
            <span className="font-medium">{confidence}%</span>
          </div> */}
          <Slider
            aria-label="Livello di confidence"
            className="w-full"
            max={100}
            step={1}
            value={[confidence]}
            disabled
            showThumb={false}
          />
        </div>

        <div className="flex flex-1 flex-col items-center justify-center gap-3 text-center">
          <CheckCircle2 className="size-48 text-green-500" aria-hidden="true" />
          <p className="text-6xl font-semibold">PUOI PROSEGUIRE</p>
        </div>
      </div>
    </div>
  )
}
