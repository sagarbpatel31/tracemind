"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Activity, ArrowRight, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { setToken, setUser, type AuthUser } from "@/lib/auth";
import { apiFetch } from "@/lib/api-client";

interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: AuthUser;
}

export default function LoginPage() {
  const router = useRouter();
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const endpoint = isRegister ? "/auth/register" : "/auth/login";
      const body = isRegister
        ? { email, password, name }
        : { email, password };

      const data = await apiFetch<TokenResponse>(endpoint, {
        method: "POST",
        body: JSON.stringify(body),
      });

      setToken(data.access_token);
      setUser(data.user);
      router.push("/dashboard");
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Something went wrong";
      if (message.includes("401")) {
        setError("Invalid email or password");
      } else if (message.includes("409")) {
        setError("Email already registered");
      } else {
        setError(message);
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="flex items-center justify-center gap-2 mb-8">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
            <Activity className="w-5 h-5 text-primary-foreground" />
          </div>
          <span className="text-lg font-bold tracking-tight">TraceMind</span>
        </div>

        <Card>
          <CardHeader className="text-center pb-4">
            <CardTitle className="text-xl">
              {isRegister ? "Create an account" : "Welcome back"}
            </CardTitle>
            <p className="text-sm text-muted-foreground">
              {isRegister
                ? "Sign up to start monitoring your robots"
                : "Sign in to your TraceMind dashboard"}
            </p>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {isRegister && (
                <div className="space-y-2">
                  <Label htmlFor="name">Name</Label>
                  <Input
                    id="name"
                    type="text"
                    placeholder="Your name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required={isRegister}
                  />
                </div>
              )}
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="you@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={4}
                />
              </div>

              {error && (
                <div className="text-sm text-red-500 bg-red-500/10 border border-red-500/20 rounded-md px-3 py-2">
                  {error}
                </div>
              )}

              <Button type="submit" className="w-full gap-2" disabled={loading}>
                {loading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <ArrowRight className="w-4 h-4" />
                )}
                {isRegister ? "Create Account" : "Sign In"}
              </Button>
            </form>

            <div className="mt-4 text-center text-sm text-muted-foreground">
              {isRegister ? (
                <>
                  Already have an account?{" "}
                  <button
                    type="button"
                    onClick={() => {
                      setIsRegister(false);
                      setError("");
                    }}
                    className="text-foreground hover:underline font-medium"
                  >
                    Sign in
                  </button>
                </>
              ) : (
                <>
                  Don&apos;t have an account?{" "}
                  <button
                    type="button"
                    onClick={() => {
                      setIsRegister(true);
                      setError("");
                    }}
                    className="text-foreground hover:underline font-medium"
                  >
                    Sign up
                  </button>
                </>
              )}
            </div>

            {/* Demo credentials hint */}
            <div className="mt-6 pt-4 border-t border-border/40 text-center">
              <p className="text-xs text-muted-foreground">
                Demo: <span className="font-mono">demo@tracemind.ai</span> /{" "}
                <span className="font-mono">demo123</span>
              </p>
            </div>
          </CardContent>
        </Card>

        <p className="mt-4 text-center text-xs text-muted-foreground">
          <Link href="/" className="hover:text-foreground transition-colors">
            Back to home
          </Link>
        </p>
      </div>
    </div>
  );
}
