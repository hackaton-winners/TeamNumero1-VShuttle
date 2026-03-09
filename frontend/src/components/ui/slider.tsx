import * as React from "react"
import { Slider as SliderPrimitive } from "radix-ui"

import { cn } from "@/lib/utils"

function Slider({
  className,
  trackClassName,
  rangeClassName,
  thumbClassName,
  value,
  defaultValue,
  showThumb = true,
  ...props
}: React.ComponentProps<typeof SliderPrimitive.Root> & {
  showThumb?: boolean
  trackClassName?: string
  rangeClassName?: string
  thumbClassName?: string
}) {
  const thumbCount = Array.isArray(value)
    ? value.length
    : Array.isArray(defaultValue)
      ? defaultValue.length
      : 1

  return (
    <SliderPrimitive.Root
      data-slot="slider"
      value={value}
      defaultValue={defaultValue}
      className={cn(
        "relative flex w-full touch-none items-center select-none",
        className
      )}
      {...props}
    >
      <SliderPrimitive.Track
        className={cn(
          "relative h-8 w-full grow overflow-hidden rounded-full bg-muted",
          trackClassName
        )}
      >
        <SliderPrimitive.Range
          className={cn(
            "absolute h-full bg-success will-change-[width,transform] motion-safe:transition-[width,transform] motion-safe:duration-100 motion-safe:ease-linear",
            rangeClassName
          )}
        />
      </SliderPrimitive.Track>
      {showThumb &&
        Array.from({ length: thumbCount }).map((_, index) => (
          <SliderPrimitive.Thumb
            key={index}
            className={cn(
              "block size-5 shrink-0 rounded-full border border-success bg-background shadow-sm ring-ring/50 transition-[color,box-shadow] hover:ring-3 focus-visible:ring-3 disabled:pointer-events-none disabled:opacity-50",
              thumbClassName
            )}
          />
        ))}
    </SliderPrimitive.Root>
  )
}

export { Slider }
