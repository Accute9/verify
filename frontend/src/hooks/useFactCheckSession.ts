import { useCallback, useRef, useState } from "react";
import type { EvalResult, RecordingStatus } from "../types";

const WS_URL = "ws://127.0.0.1:8000/ws";

interface ServerMessage {
  status?: string;
  transcription?: string;
  final_transcript?: string;
  eval_result?: EvalResult;
}

export function useFactCheckSession() {
  const [status, setStatus] = useState<RecordingStatus>("idle");
  const [transcript, setTranscript] = useState("");
  const [evalResult, setEvalResult] = useState<EvalResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const socketRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);

  const start = useCallback(async () => {
    setTranscript("");
    setEvalResult(null);
    setError(null);

    try {
      console.log("Requesting display media...");
      const stream = await navigator.mediaDevices.getDisplayMedia({
        video: true,
        audio: true,
      });
      mediaStreamRef.current = stream;
      const socket = new WebSocket(WS_URL);
      socketRef.current = socket;
      console.log("Display media stream obtained:", stream);

      socket.onclose = (e) => {
        console.log(
          "Socket closed — code:",
          e.code,
          "reason:",
          e.reason,
          "wasClean:",
          e.wasClean,
        );
        setStatus("idle");
      };

      socket.onmessage = (e) => {
        console.log("Message from server:", e.data);
        const msg: ServerMessage = JSON.parse(e.data);
        if (msg.status === "keep-alive ping") {
          return;
        }
        if (msg.transcription) {
          console.log("Transcription: ", msg.transcription);
          setTranscript((prev) => prev + msg.transcription + " ");
        } else {
          console.log("Server message:", msg);
        }
        if (msg.final_transcript) {
          console.log("Final transcript received:", msg.final_transcript);
        }
        if (msg.eval_result) {
          console.log("Evaluation result received:", msg.eval_result);
          setEvalResult(msg.eval_result);
        }
      };

      socket.onerror = (e) => {
        console.log("Socket error:", e);
      };

      socket.addEventListener("open", () => {
        const audioTracks = stream.getAudioTracks();
        console.log("Audio tracks:", audioTracks);
        if (audioTracks.length === 0) {
          console.error("No audio tracks found in the stream.");
          setError("No audio track was shared. Please include audio when sharing.");
          return;
        }
        const audioStream = new MediaStream(stream.getAudioTracks());
        const mediaRecorder = new MediaRecorder(audioStream, {
          mimeType: "audio/webm;codecs=opus",
        });
        mediaRecorderRef.current = mediaRecorder;
        mediaRecorder.addEventListener("dataavailable", (e) => {
          if (e.data.size > 0 && socket.readyState === WebSocket.OPEN) {
            socket.send(e.data);
          }
        });
        mediaRecorder.start(2000);
        setStatus("recording");
      });
    } catch (err) {
      console.error("Error accessing display media:", err);
      setError("Could not start screen/audio capture.");
    }
  }, []);

  const stop = useCallback(() => {
    console.log("Stop requested. Stopping recording and closing resources...");
    const mediaRecorder = mediaRecorderRef.current;
    const mediaStream = mediaStreamRef.current;
    const socket = socketRef.current;

    if (mediaRecorder && mediaRecorder.state !== "inactive") {
      mediaRecorder.stop();
    }
    if (mediaStream) {
      mediaStream.getTracks().forEach((track) => track.stop());
    }
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ action: "stop" }));
    }
    setStatus("idle");
  }, []);

  return { status, transcript, evalResult, error, start, stop };
}
