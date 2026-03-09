import { CircleX } from "lucide-react"

type StopProps = {
  message?: string
  subMessage?: string
}

export function Stop({
  message = "STOP",
  subMessage = "Operazione interrotta",
}: StopProps) {
  return (
    <div className="h-full w-full p-6">
      <div className="mx-auto flex h-full w-full flex-col">
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
