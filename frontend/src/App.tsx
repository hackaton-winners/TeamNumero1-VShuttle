import { Ongoing } from "./pages/Ongoing"
import { Stop } from "./pages/Stop"
import { Warning } from "./pages/Warning"

export function App() {
  return (
    <div className="h-svh w-screen p-4">
      <div className="flex h-full w-full items-center justify-center">
        {/* <Button variant={"default"} size={"lg"}>
          START SIMULATION
        </Button> */}
        {/* <Ongoing /> */}
        {/* <Stop message="NON PUOI PROSEGUIRE" /> */}
        <Warning countdownFrom={2} />
      </div>
    </div>
  )
}

export default App
