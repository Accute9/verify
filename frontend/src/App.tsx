import { useFactCheckSession } from "./hooks/useFactCheckSession";
import { TopBar } from "./components/TopBar";
import { Hero } from "./components/Hero";
import { Controls } from "./components/Controls";
import { TranscriptCard } from "./components/TranscriptCard";
import { ResultCard } from "./components/ResultCard";

function App() {
  const { status, transcript, evalResult, error, start, stop } =
    useFactCheckSession();

  return (
    <div className="flex min-h-screen flex-col">
      <TopBar status={status} />

      <main className="mx-auto w-full max-w-[1180px] flex-1 px-5 pb-15 pt-6 sm:px-10 md:px-14">
        <Hero />

        {error && (
          <div className="mx-auto mb-6 max-w-xl rounded-xl border border-red/30 bg-red/10 px-4 py-3 text-center text-sm text-red">
            {error}
          </div>
        )}

        <Controls status={status} onStart={start} onStop={stop} />

        <div className="grid grid-cols-1 gap-5.5 md:grid-cols-2">
          <TranscriptCard transcript={transcript} />
          <ResultCard result={evalResult} />
        </div>
      </main>

      <footer className="border-t border-border py-4.5 text-center text-xs text-text-faint">
        Verify — live transcription and claim verification
      </footer>
    </div>
  );
}

export default App;
