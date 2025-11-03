"use client";

import { Mic, MessageSquare, CheckCircle, Calendar } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

const steps = [
  {
    icon: Mic,
    title: "Speak Your Plans",
    description: "Tap the mic and describe your dream trip naturally. &apos;Plan a 5-day trip to Paris for two in June.&apos;",
    color: "text-blue-500",
    bgColor: "bg-blue-500/10",
  },
  {
    icon: MessageSquare,
    title: "AI Conversation",
    description: "VoycePlan asks clarifying questions and presents personalized options based on your preferences.",
    color: "text-purple-500",
    bgColor: "bg-purple-500/10",
  },
  {
    icon: CheckCircle,
    title: "Confirm Details",
    description: "Review and confirm your selections via voice. Make changes anytime by simply speaking.",
    color: "text-green-500",
    bgColor: "bg-green-500/10",
  },
  {
    icon: Calendar,
    title: "Get Your Itinerary",
    description: "Receive a complete travel plan with flights, hotels, activities, and all the details you need.",
    color: "text-pink-500",
    bgColor: "bg-pink-500/10",
  },
];

export function HowItWorksSection() {
  return (
    <section id="how-it-works" className="py-20 md:py-32 bg-secondary/30">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-4">
            How It <span className="text-primary">Works</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Planning your perfect trip is as simple as having a conversation. Here&apos;s how VoycePlan makes it effortless.
          </p>
        </div>

        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {steps.map((step, index) => (
              <div key={index} className="relative">
                <Card className="h-full hover:shadow-lg transition-shadow border-2 hover:border-primary/50">
                  <CardContent className="p-6 flex flex-col items-center text-center">
                    {/* Step Number */}
                    <div className="absolute -top-4 -left-4 w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center font-bold text-sm shadow-lg">
                      {index + 1}
                    </div>

                    {/* Icon */}
                    <div className={`${step.bgColor} p-4 rounded-full mb-4`}>
                      <step.icon className={`h-8 w-8 ${step.color}`} />
                    </div>

                    {/* Title */}
                    <h3 className="text-xl font-semibold mb-3">{step.title}</h3>

                    {/* Description */}
                    <p className="text-muted-foreground text-sm leading-relaxed">
                      {step.description}
                    </p>
                  </CardContent>
                </Card>

                {/* Connector Line (hidden on mobile and last item) */}
                {index < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-1/2 -right-4 w-8 h-0.5 bg-gradient-to-r from-primary to-transparent" />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Additional Info */}
        <div className="mt-16 text-center">
          <div className="inline-flex items-center gap-2 bg-primary/10 px-6 py-3 rounded-full">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <p className="text-sm font-medium">
              Average planning time: <span className="text-primary font-bold">3 minutes</span>
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
