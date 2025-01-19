import { useEffect, useState } from "react";

interface QueueItem {
  user_name: string;
  timestamp: string;
  status: "pending" | "processing" | "completed" | "failed";
}

interface QueueDisplayProps {
  onSetUpdate: (updateFn: () => void) => void;
}

export default function QueueDisplay({ onSetUpdate }: QueueDisplayProps) {
  const [queue, setQueue] = useState<QueueItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchQueueStatus = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/queue`
      );
      if (response.ok) {
        const data = await response.json();
        setQueue(data.queue);
      }
    } catch (error) {
      console.error("Error fetching queue:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchQueueStatus();
    onSetUpdate(fetchQueueStatus);
    const interval = setInterval(fetchQueueStatus, 5000);
    return () => clearInterval(interval);
  }, [onSetUpdate]);

  const formatTimestamp = (timestamp: string) => {
    // e.g. 2025 01 19 _ 08 57 32
    const year = timestamp.slice(0, 4);
    const month = timestamp.slice(4, 6);
    const day = timestamp.slice(6, 8);
    const hour = timestamp.slice(9, 11);
    const minute = timestamp.slice(11, 13);
    const second = timestamp.slice(13, 15);

    return `${month}/${day}/${year} ${hour}:${minute}:${second}`;
  };

  return (
    <div>
      <h2>Drawing Queue</h2>
      {isLoading ? (
        <p>Loading queue...</p>
      ) : queue.length === 0 ? (
        <p>No drawings in queue</p>
      ) : (
        <ul>
          {queue.map((item) => (
            <li key={item.timestamp}>
              <strong>Name:</strong> {item.user_name}
              {" | "}
              <strong>Time:</strong> {formatTimestamp(item.timestamp)}
              {" | "}
              <strong>Status:</strong> {item.status}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
