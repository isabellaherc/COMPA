"use client";

import { createElement, useEffect } from "react";
import { ELEVENLABS_AGENT_ID } from "@/lib/api";

/**
 * Burbuja global "Hablá con Compa" — agente conversacional real de ElevenLabs.
 * Mismo agente que hace las llamadas telefónicas (prompt v3 + tools n8n + RAG legal).
 */
export function CompaWidget() {
  useEffect(() => {
    if (document.querySelector("script[data-compa-convai]")) return;
    const s = document.createElement("script");
    s.src = "https://unpkg.com/@elevenlabs/convai-widget-embed";
    s.async = true;
    s.setAttribute("data-compa-convai", "1");
    document.body.appendChild(s);
  }, []);

  return createElement("elevenlabs-convai", { "agent-id": ELEVENLABS_AGENT_ID });
}
