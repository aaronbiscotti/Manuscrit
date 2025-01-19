"use client";

import QueueDisplay from "@/components/QueueDisplay";
import { useEffect, useRef, useState } from "react";

export default function Home() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [status, setStatus] = useState("");
  const queueUpdateRef = useRef<(() => void) | undefined>(undefined);

  const setQueueUpdate = (updateFn: () => void) => {
    queueUpdateRef.current = updateFn;
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.strokeStyle = "black";
    ctx.lineWidth = 2;
    ctx.lineCap = "round";
  }, []);

  const startDrawing = (e: React.MouseEvent | React.TouchEvent) => {
    setIsDrawing(true);
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const rect = canvas.getBoundingClientRect();
    const x =
      "touches" in e ? e.touches[0].clientX - rect.left : e.clientX - rect.left;
    const y =
      "touches" in e ? e.touches[0].clientY - rect.top : e.clientY - rect.top;

    ctx.beginPath();
    ctx.moveTo(x, y);
  };

  const draw = (e: React.MouseEvent | React.TouchEvent) => {
    if (!isDrawing) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const rect = canvas.getBoundingClientRect();
    const x =
      "touches" in e ? e.touches[0].clientX - rect.left : e.clientX - rect.left;
    const y =
      "touches" in e ? e.touches[0].clientY - rect.top : e.clientY - rect.top;

    ctx.lineTo(x, y);
    ctx.stroke();
  };

  const stopDrawing = () => {
    setIsDrawing(false);
  };

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  };

  const submitDrawing = async () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    try {
      const tempCanvas = document.createElement("canvas");
      tempCanvas.width = canvas.width;
      tempCanvas.height = canvas.height;
      const tempCtx = tempCanvas.getContext("2d");
      if (!tempCtx) return;

      // Create temp canvas
      tempCtx.fillStyle = "white";
      tempCtx.fillRect(0, 0, tempCanvas.width, tempCanvas.height);
      tempCtx.drawImage(canvas, 0, 0);

      const blob = await new Promise<Blob>((resolve) =>
        tempCanvas.toBlob((b) => resolve(b!), "image/png")
      );

      const formData = new FormData();
      formData.append("drawing", blob, "drawing.png");

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/upload`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (response.ok) {
        setStatus("Drawing submitted successfully!");
        clearCanvas();
        // Trigger queue updates
        if (queueUpdateRef.current) {
          queueUpdateRef.current();
        }
      } else {
        throw new Error("Upload failed");
      }
    } catch (error) {
      console.error("Error:", error);
      setStatus("Error submitting drawing");
    }

    setTimeout(() => setStatus(""), 3000);
  };

  return (
    <main>
      <h1>Draw Something</h1>

      <div>
        <canvas
          ref={canvasRef}
          width={300}
          height={300}
          style={{ border: "1px solid black" }}
          onMouseDown={startDrawing}
          onMouseMove={draw}
          onMouseUp={stopDrawing}
          onMouseLeave={stopDrawing}
          onTouchStart={startDrawing}
          onTouchMove={draw}
          onTouchEnd={stopDrawing}
        />

        <div>
          <button onClick={clearCanvas}>Clear</button>
          <button onClick={submitDrawing}>Submit</button>
        </div>

        {status && <p>{status}</p>}
      </div>

      <QueueDisplay onSetUpdate={setQueueUpdate} />
    </main>
  );
}
