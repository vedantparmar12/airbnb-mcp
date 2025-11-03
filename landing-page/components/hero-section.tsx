"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { ArrowDown, Mic } from "lucide-react";
import Link from "next/link";
import { useAuth } from "@/contexts/auth-context";

export function HeroSection() {
  useEffect(() => {
    // Initialize unicorn.studio background
    if (!window.UnicornStudio) {
      window.UnicornStudio = { isInitialized: false };
      const script = document.createElement("script");
      script.src = "https://cdn.jsdelivr.net/gh/hiunicornstudio/unicornstudio.js@v1.4.33/dist/unicornStudio.umd.js";
      script.onload = function() {
        if (window.UnicornStudio && !window.UnicornStudio.isInitialized) {
          (window as any).UnicornStudio.init();
          window.UnicornStudio.isInitialized = true;
        }
      };
      (document.head || document.body).appendChild(script);
    }
  }, []);

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-primary via-purple-600 to-pink-600">
      {/* Unicorn Studio Background */}
      <div
        data-us-project="hM0IOnVmbaE8UjRulsyU"
        className="absolute inset-0 z-0"
        style={{
          width: "100%",
          height: "100%",
        }}
      />

      {/* Content */}
      <div className="relative z-10 container mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-32">
        <div className="max-w-2xl">
          {/* Headline */}
          <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold mb-6 leading-tight">
            <span className="bg-gradient-to-r from-primary via-purple-600 to-pink-600 bg-clip-text text-transparent">
              Plan Your Next Trip,
            </span>
            <br />
            <span className="text-foreground">Just by Talking</span>
          </h1>

          {/* Subheading */}
          <p className="text-lg sm:text-xl md:text-2xl text-white mb-12">
            Meet VoycePlan, your AI travel agent. Describe your dream trip, and let us handle the details.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 mb-16">
            <Link href="/signin">
              <Button size="lg" className="w-full sm:w-auto text-lg px-8 py-6">
                <Mic className="mr-2 h-5 w-5" />
                Get Started Free
              </Button>
            </Link>
            <a href="#how-it-works">
              <Button size="lg" variant="outline" className="w-full sm:w-auto text-lg px-8 py-6">
                Learn More
              </Button>
            </a>
          </div>

          {/* Quick Info */}
          <div className="flex flex-wrap gap-6 text-sm text-white/80">
            <div className="flex items-center gap-2">
              <span className="text-primary text-xl">✓</span>
              <span>10 free voice sessions</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-primary text-xl">✓</span>
              <span>No credit card required</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-primary text-xl">✓</span>
              <span>Sign in with Google</span>
            </div>
          </div>

          {/* Scroll Indicator */}
          <div className="flex justify-start animate-bounce">
            <a
              href="#how-it-works"
              className="flex flex-col items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              <span>Discover how it works</span>
              <ArrowDown className="h-5 w-5" />
            </a>
          </div>
        </div>
      </div>

      {/* Gradient overlay for better text readability */}
      <div className="absolute inset-0 bg-gradient-to-b from-background/50 via-transparent to-background pointer-events-none" />
    </section>
  );
}
