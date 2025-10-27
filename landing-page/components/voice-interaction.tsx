"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Mic, MicOff, Loader2, LogOut } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/contexts/auth-context";
import { GoogleLogin, CredentialResponse } from "@react-oauth/google";
import {
  LiveKitRoom,
  useVoiceAssistant,
  BarVisualizer,
  RoomAudioRenderer,
  VoiceAssistantControlBar,
  DisconnectButton,
} from "@livekit/components-react";
import "@livekit/components-styles";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function VoiceInteraction() {
  const { user, accessToken, login, logout, refreshUser, isLoading } = useAuth();
  const [livekitToken, setLivekitToken] = useState<string | null>(null);
  const [livekitUrl, setLivekitUrl] = useState<string | null>(null);
  const [roomName, setRoomName] = useState<string | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGoogleLogin = async (credentialResponse: CredentialResponse) => {
    if (!credentialResponse.credential) return;
    
    try {
      await login(credentialResponse.credential);
      setError(null);
    } catch (err) {
      setError("Login failed. Please try again.");
      console.error(err);
    }
  };

  const startVoiceSession = async () => {
    if (!user || !accessToken) return;
    
    setIsConnecting(true);
    setError(null);
    
    try {
      // Request LiveKit token from backend
      const response = await fetch(`${API_BASE_URL}/livekit/token`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({}),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to get access token");
      }
      
      const data = await response.json();
      setLivekitToken(data.token);
      setLivekitUrl(data.url);
      setRoomName(data.room_name);
      
      // Refresh user credits
      await refreshUser();
    } catch (err: any) {
      setError(err.message || "Failed to start voice session");
      console.error(err);
    } finally {
      setIsConnecting(false);
    }
  };

  const disconnectSession = () => {
    setLivekitToken(null);
    setLivekitUrl(null);
    setRoomName(null);
    refreshUser();
  };

  // Show loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  // Show login if not authenticated
  if (!user) {
    return (
      <div className="w-full max-w-2xl">
        <div className="text-center p-8 bg-secondary/50 rounded-lg">
          <h3 className="text-xl font-semibold mb-4">Sign in to Start Planning</h3>
          <p className="text-muted-foreground mb-6">
            Sign in with your Google account to get 10 free voice planning sessions.
          </p>
          <div className="flex justify-center">
            <GoogleLogin
              onSuccess={handleGoogleLogin}
              onError={() => setError("Login failed")}
              theme="outline"
              size="large"
            />
          </div>
          {error && (
            <p className="text-red-500 mt-4 text-sm">{error}</p>
          )}
        </div>
      </div>
    );
  }

  // Show LiveKit room if connected
  if (livekitToken && livekitUrl && roomName) {
    return (
      <div className="w-full max-w-2xl">
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            {user.picture && (
              <img
                src={user.picture}
                alt={user.name || user.email}
                className="w-10 h-10 rounded-full"
              />
            )}
            <div>
              <p className="font-medium">{user.name || user.email}</p>
              <p className="text-sm text-muted-foreground">
                Credits remaining: {user.credits}
              </p>
            </div>
          </div>
          <Button variant="outline" size="sm" onClick={logout}>
            <LogOut className="h-4 w-4 mr-2" />
            Logout
          </Button>
        </div>

        <LiveKitRoom
          token={livekitToken}
          serverUrl={livekitUrl}
          connect={true}
          audio={true}
          video={false}
          onDisconnected={disconnectSession}
          className="rounded-lg bg-secondary/50 p-6"
        >
          <SimpleVoiceAssistant />
          <RoomAudioRenderer />
        </LiveKitRoom>
      </div>
    );
  }

  // Show start session button if authenticated but not connected
  return (
    <div className="w-full max-w-2xl">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          {user.picture && (
            <img
              src={user.picture}
              alt={user.name || user.email}
              className="w-10 h-10 rounded-full"
            />
          )}
          <div>
            <p className="font-medium">{user.name || user.email}</p>
            <p className="text-sm text-muted-foreground">
              Credits remaining: {user.credits}
            </p>
          </div>
        </div>
        <Button variant="outline" size="sm" onClick={logout}>
          <LogOut className="h-4 w-4 mr-2" />
          Logout
        </Button>
      </div>

      <div className="text-center p-8 bg-secondary/50 rounded-lg">
        <div className="mb-6">
          <Mic className="h-20 w-20 mx-auto text-primary mb-4" />
          <h3 className="text-xl font-semibold mb-2">Ready to Plan Your Trip?</h3>
          <p className="text-muted-foreground">
            Click the button below to start a voice conversation with your AI travel assistant.
          </p>
        </div>

        <Button
          onClick={startVoiceSession}
          disabled={isConnecting || user.credits <= 0}
          size="lg"
          className="min-w-[200px]"
        >
          {isConnecting ? (
            <>
              <Loader2 className="h-5 w-5 mr-2 animate-spin" />
              Connecting...
            </>
          ) : (
            <>
              <Mic className="h-5 w-5 mr-2" />
              Start Voice Session
            </>
          )}
        </Button>

        {user.credits <= 0 && (
          <p className="text-red-500 mt-4 text-sm">
            You have no credits remaining. Please contact support.
          </p>
        )}

        {error && (
          <p className="text-red-500 mt-4 text-sm">{error}</p>
        )}

        <div className="mt-6 text-left">
          <p className="text-sm font-medium text-muted-foreground mb-2">
            What you can ask:
          </p>
          <ul className="text-sm text-muted-foreground space-y-1">
            <li>• "Find me Airbnb listings in Paris"</li>
            <li>• "Show me beach properties under $150 per night"</li>
            <li>• "Compare these two listings for me"</li>
            <li>• "Calculate the total cost for a 5-day trip"</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

// Simple voice assistant UI component
function SimpleVoiceAssistant() {
  const { state, audioTrack } = useVoiceAssistant();
  const [userTranscript, setUserTranscript] = useState("");
  const [agentResponse, setAgentResponse] = useState("");

  // Listen for transcription events from the room
  useEffect(() => {
    const handleTranscription = (transcription: any) => {
      if (transcription.participant?.identity !== "agent") {
        // User transcript
        setUserTranscript(transcription.text);
      } else {
        // Agent response
        setAgentResponse(transcription.text);
      }
    };

    // Note: This is a simplified version - actual implementation would use LiveKit's transcription events
    // For now, transcripts will appear in the UI based on state changes
    
    return () => {
      // Cleanup
    };
  }, []);

  return (
    <div className="flex flex-col items-center gap-6 w-full">
      <div className="text-center">
        <h3 className="text-lg font-semibold mb-2">
          {state === "listening" && "🎤 Listening..."}
          {state === "thinking" && "🤔 Processing..."}
          {state === "speaking" && "🗣️ VoycePlan is responding..."}
          {state === "idle" && "💬 Say something to start"}
        </h3>
        <p className="text-sm text-muted-foreground">
          Speak naturally about your travel plans. Pause for 1.5 seconds to finish.
        </p>
      </div>

      {/* Audio visualizer */}
      <div className="w-full max-w-md h-24 flex items-center justify-center">
        {audioTrack && <BarVisualizer state={state} barCount={5} trackRef={audioTrack} />}
      </div>

      {/* Transcript Display */}
      <div className="w-full max-w-2xl space-y-4">
        {/* User transcript */}
        {userTranscript && state !== "idle" && (
          <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
            <p className="text-xs font-semibold text-blue-600 dark:text-blue-400 mb-1">You said:</p>
            <p className="text-sm">{userTranscript}</p>
          </div>
        )}

        {/* Agent response */}
        {agentResponse && state === "speaking" && (
          <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 border border-green-200 dark:border-green-800">
            <p className="text-xs font-semibold text-green-600 dark:text-green-400 mb-1">VoycePlan:</p>
            <p className="text-sm">{agentResponse}</p>
          </div>
        )}
      </div>

      {/* Tips */}
      <div className="text-center text-xs text-muted-foreground">
        <p>💡 Tip: Pause for 1.5 seconds after speaking to let the AI process your full sentence</p>
      </div>

      {/* Disconnect button */}
      <DisconnectButton className="lk-button lk-disconnect-button">
        <MicOff className="h-5 w-5 mr-2" />
        End Session
      </DisconnectButton>
    </div>
  );
}
