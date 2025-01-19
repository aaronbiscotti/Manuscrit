"use client";

import QueueDisplay from "@/components/QueueDisplay";
import { useEffect, useRef, useState } from "react";

export default function Home() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [status, setStatus] = useState("");
  const [userName, setUserName] = useState("");

  const queueUpdateRef = useRef<(() => void) | undefined>(undefined);

  //Setter for the queue update
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

  // If canvas is all white then return true
  const isCanvasBlank = (canvas: HTMLCanvasElement): boolean => {
    const blank = document.createElement("canvas");
    blank.width = canvas.width;
    blank.height = canvas.height;

    const bctx = blank.getContext("2d");
    if (!bctx) return false;
    bctx.fillStyle = "white";
    bctx.fillRect(0, 0, blank.width, blank.height);

    return blank.toDataURL() === canvas.toDataURL();
  };

  const submitDrawing = async () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    // 1) Check name
    if (!userName.trim()) {
      setStatus("Name is required!");
      return;
    }

    // 2) Check blank canvas
    if (isCanvasBlank(canvas)) {
      setStatus("Canvas is blank. Please draw something!");
      return;
    }

    try {
      // Copy current drawing to a temp canvas
      const tempCanvas = document.createElement("canvas");
      tempCanvas.width = canvas.width;
      tempCanvas.height = canvas.height;

      const tempCtx = tempCanvas.getContext("2d");
      if (!tempCtx) return;

      // Fill temp with white
      tempCtx.fillStyle = "white";
      tempCtx.fillRect(0, 0, tempCanvas.width, tempCanvas.height);
      // Copy user's drawing
      tempCtx.drawImage(canvas, 0, 0);

      // Convert to a Blob
      const blob = await new Promise<Blob>((resolve) =>
        tempCanvas.toBlob((b) => resolve(b!), "image/png")
      );

      // Build form data with "name" and "drawing"
      const formData = new FormData();
      formData.append("name", userName);
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
        const data = await response.json();
        setStatus(`Error: ${data?.error || "Upload failed"}`);
      }
    } catch (error) {
      console.error("Error:", error);
      setStatus("Error submitting drawing");
    }

    setTimeout(() => setStatus(""), 3000);
  };

  return (
    <main style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      <h1>Draw Something</h1>

      {/* Name field */}
      <div>
        <label htmlFor="nameInput">Name: </label>
        <input
          id="nameInput"
          type="text"
          value={userName}
          onChange={(e) => setUserName(e.target.value)}
          placeholder="Enter your name"
          required
        />
      </div>

      <div>
        <canvas
          ref={canvasRef}
          width={300}
          height={300}
          style={{
            border: "1px solid black",
            touchAction: "none",
            userSelect: "none",
          }}
          onMouseDown={startDrawing}
          onMouseMove={draw}
          onMouseUp={stopDrawing}
          onMouseLeave={stopDrawing}
          onTouchStart={startDrawing}
          onTouchMove={draw}
          onTouchEnd={stopDrawing}
        />
      </div>

      <div>
        <button onClick={clearCanvas}>Clear</button>
        <button onClick={submitDrawing}>Submit</button>
      </div>

      {status && <p style={{ color: "red" }}>{status}</p>}

      <QueueDisplay onSetUpdate={setQueueUpdate} />
    </main>
  );
}
