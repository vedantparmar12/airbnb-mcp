"use client";

import { MessageCircle, Plane, MapPin, Calendar, DollarSign, Zap } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const features = [
  {
    icon: MessageCircle,
    title: "Natural Conversation",
    description: "Plan complex trips using everyday language. No forms, no complicated menus—just talk.",
    gradient: "from-blue-500 to-cyan-500",
  },
  {
    icon: Plane,
    title: "Flight & Hotel Booking",
    description: "Finds and suggests the best flight and accommodation options based on your criteria and budget.",
    gradient: "from-purple-500 to-pink-500",
  },
  {
    icon: MapPin,
    title: "Activity Recommendations",
    description: "Discover tours, restaurants, attractions, and hidden gems tailored to your interests.",
    gradient: "from-green-500 to-emerald-500",
  },
  {
    icon: Calendar,
    title: "Itinerary Management",
    description: "Organizes your entire trip plan in one place with day-by-day schedules and bookings.",
    gradient: "from-orange-500 to-red-500",
  },
  {
    icon: DollarSign,
    title: "Real-time Information",
    description: "Access up-to-date pricing, availability, and travel advisories for informed decisions.",
    gradient: "from-yellow-500 to-orange-500",
  },
  {
    icon: Zap,
    title: "Instant Modifications",
    description: "Change your plans on the fly with simple voice commands. Flexibility at your fingertips.",
    gradient: "from-indigo-500 to-purple-500",
  },
];

export function FeaturesSection() {
  return (
    <section id="features" className="py-20 md:py-32 bg-background">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-4">
            Powerful <span className="text-primary">Features</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Everything you need to plan the perfect trip, powered by advanced AI and voice technology.
          </p>
        </div>

        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <Card
                key={index}
                className="group hover:shadow-xl transition-all duration-300 hover:-translate-y-1 border-2 hover:border-primary/50"
              >
                <CardHeader>
                  <div className="flex items-start gap-4">
                    <div className={`bg-gradient-to-br ${feature.gradient} p-3 rounded-lg shadow-lg group-hover:scale-110 transition-transform`}>
                      <feature.icon className="h-6 w-6 text-white" />
                    </div>
                    <div className="flex-1">
                      <CardTitle className="text-xl mb-2">{feature.title}</CardTitle>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base leading-relaxed">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Trust Indicators */}
        <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto">
          <div className="text-center">
            <div className="text-3xl font-bold text-primary mb-1">50K+</div>
            <div className="text-sm text-muted-foreground">Trips Planned</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-primary mb-1">4.9/5</div>
            <div className="text-sm text-muted-foreground">User Rating</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-primary mb-1">200+</div>
            <div className="text-sm text-muted-foreground">Destinations</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-primary mb-1">24/7</div>
            <div className="text-sm text-muted-foreground">AI Support</div>
          </div>
        </div>
      </div>
    </section>
  );
}
