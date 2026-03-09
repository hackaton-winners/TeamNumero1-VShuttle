import { useCallback, useEffect, useRef, useState } from "react"
import { Button } from "./components/ui/button"
import { Ongoing } from "./pages/Ongoing"
import { Stop } from "./pages/Stop"
import { Warning } from "./pages/Warning"

type Scenario = {
  id_scenario: number
  action: "GO" | "STOP" | "HUMAN_CONFIRM"
  confidence: number
  reason: string
}

type Phase = "start" | "running" | "done"

const SCENARIO_DURATION = 4000 // 4s per scenario
const HUMAN_CONFIRM_TIMEOUT = 2000 // 2s per decidere

export function App() {
  const [phase, setPhase] = useState<Phase>("start")
  const [scenarios, setScenarios] = useState<Scenario[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [waitingHuman, setWaitingHuman] = useState(false)
  const [humanTimedOut, setHumanTimedOut] = useState(false)
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const clearTimer = () => {
    if (timerRef.current) {
      clearTimeout(timerRef.current)
      timerRef.current = null
    }
  }

  const advanceToNext = useCallback(() => {
    clearTimer()
    setWaitingHuman(false)
    setHumanTimedOut(false)
    setCurrentIndex((prev) => {
      const next = prev + 1
      if (next >= scenarios.length) {
        setPhase("done")
        return prev
      }
      return next
    })
  }, [scenarios.length])

  // Fetch scenari e avvia la simulazione
  async function handleStart() {
    setError(null)
    try {
      const res = await fetch("/api/scenarios")
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data: Scenario[] = await res.json()
      if (data.length === 0) {
        setError("Nessuno scenario ricevuto dal backend")
        return
      }
      setScenarios(data)
      setCurrentIndex(0)
      setWaitingHuman(false)
      setHumanTimedOut(false)
      setPhase("running")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Errore di connessione")
    }
  }

  // Timer per avanzare automaticamente tra scenari
  useEffect(() => {
    if (phase !== "running") return
    if (currentIndex >= scenarios.length) return

    const scenario = scenarios[currentIndex]

    if (scenario.action === "HUMAN_CONFIRM") {
      // Marco ha 2 secondi per decidere
      setWaitingHuman(true)
      setHumanTimedOut(false)
      timerRef.current = setTimeout(() => {
        // Timeout scaduto → frenata d'emergenza (STOP), poi avanza
        setHumanTimedOut(true)
        setWaitingHuman(false)
        timerRef.current = setTimeout(advanceToNext, SCENARIO_DURATION)
      }, HUMAN_CONFIRM_TIMEOUT)
    } else {
      // GO o STOP: mostra per 4s poi avanza
      setWaitingHuman(false)
      setHumanTimedOut(false)
      timerRef.current = setTimeout(advanceToNext, SCENARIO_DURATION)
    }

    return clearTimer
  }, [phase, currentIndex, scenarios, advanceToNext])

  // Azione di Marco durante HUMAN_CONFIRM
  function handleHumanDecision(override: boolean) {
    if (!waitingHuman) return
    clearTimer()
    setWaitingHuman(false)

    if (override) {
      // Marco conferma il passaggio → mostra GO brevemente
      setScenarios((prev) => {
        const updated = [...prev]
        updated[currentIndex] = { ...updated[currentIndex], action: "GO" }
        return updated
      })
    } else {
      // Marco arresta → mostra STOP
      setScenarios((prev) => {
        const updated = [...prev]
        updated[currentIndex] = { ...updated[currentIndex], action: "STOP" }
        return updated
      })
    }

    // Mostra risultato per 4s poi avanza
    timerRef.current = setTimeout(advanceToNext, SCENARIO_DURATION)
  }

  // ─── SCHERMATA START ─────────────────────────────────────────────
  if (phase === "start") {
    return (
      <div className="h-svh w-screen p-4">
        <div className="flex h-full w-full flex-col items-center justify-center gap-6">
          <Button variant="default" size="lg" onClick={handleStart}>
            START SIMULATION
          </Button>
          {error && <p className="text-xl text-destructive">{error}</p>}
        </div>
      </div>
    )
  }

  // ─── SCHERMATA FINE ──────────────────────────────────────────────
  if (phase === "done") {
    return (
      <div className="h-svh w-screen p-4">
        <div className="flex h-full w-full flex-col items-center justify-center gap-6">
          <p className="text-4xl font-semibold">Simulazione completata</p>
          <p className="text-xl text-muted-foreground">
            {scenarios.length} scenari elaborati
          </p>
          <Button variant="default" size="lg" onClick={() => setPhase("start")}>
            RICOMINCIA
          </Button>
        </div>
      </div>
    )
  }

  // ─── SCHERMATA RUNNING ───────────────────────────────────────────
  const scenario = scenarios[currentIndex]
  const confidencePercent = Math.round(scenario.confidence * 100)

  // Se il tempo è scaduto su HUMAN_CONFIRM → mostra STOP (frenata d'emergenza)
  if (humanTimedOut) {
    return (
      <div className="h-svh w-screen p-4">
        <Stop
          message="FRENATA D'EMERGENZA"
          subMessage="Tempo scaduto — arresto automatico"
          confidence={confidencePercent}
        />
      </div>
    )
  }

  return (
    <div className="h-svh w-screen p-4">
      {scenario.action === "GO" && <Ongoing confidence={confidencePercent} />}
      {scenario.action === "STOP" && (
        <Stop
          message="NON PUOI PROSEGUIRE"
          subMessage={scenario.reason}
          confidence={confidencePercent}
        />
      )}
      {scenario.action === "HUMAN_CONFIRM" && (
        <Warning
          message="ATTENZIONE"
          subMessage={scenario.reason}
          countdownFrom={2}
          confidence={confidencePercent}
          onOverride={() => handleHumanDecision(true)}
          onStop={() => handleHumanDecision(false)}
        />
      )}
    </div>
  )
}

export default App
