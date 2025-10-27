"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { GoogleLogin, CredentialResponse } from "@react-oauth/google";
import { useAuth } from "@/contexts/auth-context";
import { Button } from "@/components/ui/button";
import { Loader2, ArrowLeft } from "lucide-react";
import Link from "next/link";

export default function SignInPage() {
  const { user, login, isLoading } = useAuth();
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [isAuthenticating, setIsAuthenticating] = useState(false);

  // Redirect if already logged in
  useEffect(() => {
    if (user && !isLoading) {
      router.push("/voice");
    }
  }, [user, isLoading, router]);

  const handleGoogleLogin = async (credentialResponse: CredentialResponse) => {
    if (!credentialResponse.credential) return;

    setIsAuthenticating(true);
    setError(null);

    try {
      await login(credentialResponse.credential);
      // Will redirect via useEffect after successful login
    } catch (err: any) {
      setError(err.message || "Login failed. Please try again.");
      console.error(err);
    } finally {
      setIsAuthenticating(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <Link href="/" className="flex items-center text-sm text-muted-foreground hover:text-foreground">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Home
          </Link>
        </div>
      </header>

      {/* Sign In Content */}
      <div className="flex-1 flex items-center justify-center px-4">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold mb-3">Welcome to VoycePlan</h1>
            <p className="text-lg text-muted-foreground">
              Sign in to start planning your perfect trip with AI
            </p>
          </div>

          <div className="bg-card border rounded-lg p-8 shadow-lg">
            <div className="space-y-6">
              {/* Benefits */}
              <div className="space-y-3">
                <h2 className="font-semibold text-lg">What you&apos;ll get:</h2>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-start">
                    <span className="text-primary mr-2">✓</span>
                    <span>10 free voice planning sessions</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-primary mr-2">✓</span>
                    <span>AI-powered Airbnb search and recommendations</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-primary mr-2">✓</span>
                    <span>Natural voice conversations with your travel assistant</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-primary mr-2">✓</span>
                    <span>Real-time property comparisons and price analysis</span>
                  </li>
                </ul>
              </div>

              {/* Divider */}
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t"></div>
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-card px-2 text-muted-foreground">Sign in with</span>
                </div>
              </div>

              {/* Google Sign In */}
              <div className="flex flex-col items-center space-y-4">
                {isAuthenticating ? (
                  <Button disabled className="w-full">
                    <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                    Signing in...
                  </Button>
                ) : (
                  <div className="flex justify-center">
                    <GoogleLogin
                      onSuccess={handleGoogleLogin}
                      onError={() => setError("Google sign-in failed")}
                      theme="outline"
                      size="large"
                      text="signin_with"
                      shape="rectangular"
                      width="300"
                    />
                  </div>
                )}

                {error && (
                  <div className="w-full p-3 bg-destructive/10 border border-destructive/20 rounded-md">
                    <p className="text-sm text-destructive text-center">{error}</p>
                  </div>
                )}
              </div>

              {/* Terms */}
              <p className="text-xs text-center text-muted-foreground">
                By signing in, you agree to our Terms of Service and Privacy Policy
              </p>
            </div>
          </div>

          {/* Footer Info */}
          <div className="mt-6 text-center">
            <p className="text-sm text-muted-foreground">
              One Gmail account = 10 free voice sessions
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
