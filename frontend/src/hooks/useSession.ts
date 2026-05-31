"use client";

import { useEffect, useState } from "react";

function generateId(): string {
  return crypto.randomUUID();
}

export function useSession(): string {
  const [sessionId, setSessionId] = useState<string>("");

  useEffect(() => {
    const stored = localStorage.getItem("resume_tailer_session");
    if (stored) {
      setSessionId(stored);
    } else {
      const id = generateId();
      localStorage.setItem("resume_tailer_session", id);
      setSessionId(id);
    }
  }, []);

  return sessionId;
}
