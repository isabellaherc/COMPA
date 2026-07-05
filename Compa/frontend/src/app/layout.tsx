import type { Metadata } from "next";
import { Space_Grotesk, Inter } from "next/font/google";
import { Canopy } from "@/components/layout/Canopy";
import { Nav } from "@/components/layout/Nav";
import { Footer } from "@/components/layout/Footer";
import "./globals.css";

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-space",
  display: "swap",
});

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "Compa | Asesor de compras publicas para MYPE",
    template: "%s | Compa",
  },
  description:
    "Compa detecta oportunidades de COMPRASAL, las explica por voz y reta decisiones de productores salvadorenos antes de ofertar.",
  icons: {
    icon: "/icon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es" className={`${spaceGrotesk.variable} ${inter.variable}`}>
      <body className="font-sans">
        <Canopy />
        <Nav />
        <main className="min-h-[60dvh]">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
