"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Palmtree, Users, Mountain, Briefcase, Heart, Globe } from "lucide-react";

const useCases = [
  {
    icon: Palmtree,
    title: "Weekend Getaway",
    description: "Quick escapes to nearby destinations",
    example: "Find me a relaxing beach resort within 3 hours of NYC for this weekend",
    gradient: "from-cyan-500 to-blue-500",
    image: "bg-gradient-to-br from-cyan-100 to-blue-100 dark:from-cyan-950 dark:to-blue-950",
  },
  {
    icon: Users,
    title: "Family Vacation",
    description: "Kid-friendly destinations and activities",
    example: "Plan a 7-day family trip to Orlando with activities for kids aged 5 and 8",
    gradient: "from-purple-500 to-pink-500",
    image: "bg-gradient-to-br from-purple-100 to-pink-100 dark:from-purple-950 dark:to-pink-950",
  },
  {
    icon: Mountain,
    title: "Adventure Travel",
    description: "Thrilling experiences and outdoor activities",
    example: "I want a 10-day hiking and camping adventure in the Rocky Mountains",
    gradient: "from-green-500 to-emerald-500",
    image: "bg-gradient-to-br from-green-100 to-emerald-100 dark:from-green-950 dark:to-emerald-950",
  },
  {
    icon: Briefcase,
    title: "Business Trip",
    description: "Efficient planning for work travel",
    example: "Book flights and hotel near convention center in Chicago for next Tuesday",
    gradient: "from-gray-600 to-gray-800",
    image: "bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-900 dark:to-gray-950",
  },
  {
    icon: Heart,
    title: "Romantic Escape",
    description: "Perfect getaways for couples",
    example: "Plan a romantic 5-day trip to Paris with fine dining and luxury accommodation",
    gradient: "from-red-500 to-pink-500",
    image: "bg-gradient-to-br from-red-100 to-pink-100 dark:from-red-950 dark:to-pink-950",
  },
  {
    icon: Globe,
    title: "World Explorer",
    description: "Multi-city and international journeys",
    example: "Create a 3-week backpacking itinerary through Southeast Asia under $2000",
    gradient: "from-orange-500 to-yellow-500",
    image: "bg-gradient-to-br from-orange-100 to-yellow-100 dark:from-orange-950 dark:to-yellow-950",
  },
];

export function UseCasesSection() {
  const [selectedCase, setSelectedCase] = useState<number | null>(null);

  return (
    <section id="use-cases" className="py-20 md:py-32 bg-secondary/30">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-4">
            Perfect for <span className="text-primary">Every Journey</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Whatever type of trip you&apos;re dreaming of, VoycePlan makes planning effortless and exciting.
          </p>
        </div>

        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {useCases.map((useCase, index) => (
              <Card
                key={index}
                className={`group cursor-pointer transition-all duration-300 hover:-translate-y-2 hover:shadow-2xl ${
                  selectedCase === index ? "ring-2 ring-primary shadow-xl" : ""
                }`}
                onClick={() => setSelectedCase(selectedCase === index ? null : index)}
              >
                <CardHeader>
                  <div className={`${useCase.image} p-8 rounded-lg mb-4 flex items-center justify-center`}>
                    <div className={`bg-gradient-to-br ${useCase.gradient} p-4 rounded-full shadow-lg group-hover:scale-110 transition-transform`}>
                      <useCase.icon className="h-8 w-8 text-white" />
                    </div>
                  </div>
                  <CardTitle className="text-xl">{useCase.title}</CardTitle>
                  <CardDescription className="text-sm">
                    {useCase.description}
                  </CardDescription>
                </CardHeader>

                {selectedCase === index && (
                  <CardContent className="pt-0">
                    <div className="bg-primary/10 border border-primary/20 rounded-lg p-4">
                      <p className="text-sm font-medium mb-2 text-primary">Try saying:</p>
                      <p className="text-sm italic">&quot;{useCase.example}&quot;</p>
                    </div>
                  </CardContent>
                )}
              </Card>
            ))}
          </div>
        </div>

        {/* CTA */}
        <div className="mt-16 text-center">
          <p className="text-lg text-muted-foreground mb-6">
            Ready to explore? Start planning your dream trip now.
          </p>
          <Button size="lg" className="shadow-lg shadow-primary/30">
            Try VoycePlan Free
          </Button>
        </div>
      </div>
    </section>
  );
}
