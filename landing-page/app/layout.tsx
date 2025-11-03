import type { Metadata } from "next";
import { Plus_Jakarta_Sans, Lora, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

const plusJakartaSans = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-sans",
});

const lora = Lora({
  subsets: ["latin"],
  variable: "--font-serif",
});

const ibmPlexMono = IBM_Plex_Mono({
  weight: ["400", "500", "600", "700"],
  subsets: ["latin"],
  variable: "--font-mono",
});

export const metadata: Metadata = {
  title: "VoycePlan - AI-Powered Voice Travel Planning",
  description: "Plan your perfect trip just by talking. VoycePlan is your AI travel agent that understands natural conversation and creates personalized itineraries in minutes.",
  keywords: ["travel planning", "AI travel agent", "voice assistant", "trip planner", "vacation planning"],
  authors: [{ name: "VoycePlan" }],
  openGraph: {
    title: "VoycePlan - Plan Your Next Trip, Just by Talking",
    description: "Your AI-powered voice travel agent. Describe your dream trip, and let us handle the details.",
    type: "website",
    locale: "en_US",
  },
  twitter: {
    card: "summary_large_image",
    title: "VoycePlan - AI-Powered Voice Travel Planning",
    description: "Plan your perfect trip just by talking. Your AI travel agent that understands you.",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className={`${plusJakartaSans.variable} ${lora.variable} ${ibmPlexMono.variable} font-sans`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
