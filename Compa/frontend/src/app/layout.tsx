import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Compa | Asesor de compras públicas para MYPE",
  description:
    "Compa detecta oportunidades de COMPRASAL, las explica por voz y reta decisiones de productores salvadoreños antes de ofertar.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
