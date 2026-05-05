import Link from "next/link";
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  Cpu,
  FileSearch,
  Layers,
  Radio,
  RefreshCw,
  Search,
  Zap,
} from "lucide-react";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Nav */}
      <nav className="border-b border-border/40 backdrop-blur-sm sticky top-0 z-50 bg-background/80">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
              <Activity className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="text-lg font-bold tracking-tight">Watchpoint</span>
          </div>
          <div className="flex items-center gap-4">
            <Link
              href="/dashboard"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              Dashboard
            </Link>
            <Link href="/dashboard" className={cn(buttonVariants({ size: "sm" }))}>
              View Demo
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="py-24 md:py-32">
        <div className="max-w-6xl mx-auto px-6">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-border/60 text-xs text-muted-foreground mb-6">
              <Radio className="w-3 h-3 text-green-500 animate-pulse" />
              Now monitoring ROS2 systems
            </div>
            <h1 className="text-4xl md:text-6xl font-bold tracking-tight leading-[1.1] mb-6">
              Stop guessing why
              <br />
              your robot failed.
            </h1>
            <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mb-8 leading-relaxed">
              Watchpoint captures incidents, correlates telemetry across your
              entire stack, and generates replayable failure bundles with
              AI-assisted root-cause analysis. Built for ROS2 and edge AI teams.
            </p>
            <div className="flex flex-wrap gap-4">
              <Link href="/dashboard" className={cn(buttonVariants({ size: "lg" }), "gap-2")}>
                View Live Demo
                <ArrowRight className="w-4 h-4" />
              </Link>
              <a href="#architecture" className={cn(buttonVariants({ variant: "outline", size: "lg" }), "gap-2")}>
                How It Works
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Stats bar */}
      <section className="border-y border-border/40">
        <div className="max-w-6xl mx-auto px-6 py-8 grid grid-cols-2 md:grid-cols-4 gap-8">
          {[
            { label: "Incidents Captured", value: "10K+" },
            { label: "MTTR Reduction", value: "73%" },
            { label: "Supported Platforms", value: "5+" },
            { label: "Replay Bundles", value: "Instant" },
          ].map((stat) => (
            <div key={stat.label}>
              <div className="text-2xl md:text-3xl font-bold">{stat.value}</div>
              <div className="text-sm text-muted-foreground mt-1">
                {stat.label}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="py-24">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4">
              From failure to root cause in minutes
            </h2>
            <p className="text-muted-foreground max-w-xl mx-auto">
              Watchpoint connects every signal — logs, metrics, ROS topics,
              inference timing, hardware state — into one incident timeline.
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <FeatureCard
              icon={<AlertTriangle className="w-5 h-5" />}
              title="Incident Capture"
              description="Automatic triggers on node crashes, topic drops, thermal throttling, and custom conditions. Captures pre/during/post context."
            />
            <FeatureCard
              icon={<Search className="w-5 h-5" />}
              title="Root Cause Analysis"
              description="Rules-based engine correlates signals to identify resource contention, thermal throttling, version regressions, and failure chains."
            />
            <FeatureCard
              icon={<RefreshCw className="w-5 h-5" />}
              title="Replay Bundles"
              description="Download portable .zip bundles with all incident evidence. Share with any engineer — they know where to start."
            />
            <FeatureCard
              icon={<Layers className="w-5 h-5" />}
              title="ROS2 Native"
              description="Deep integration with ROS2 topics, nodes, and services. Monitor publish rates, message lag, and node health in real time."
            />
          </div>
        </div>
      </section>

      {/* Architecture */}
      <section id="architecture" className="py-24 border-t border-border/40">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4">Architecture</h2>
            <p className="text-muted-foreground max-w-xl mx-auto">
              Lightweight edge agent, powerful cloud analysis, beautiful
              investigation UI.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <ArchBlock
              icon={<Cpu className="w-6 h-6" />}
              title="Edge Agent"
              items={[
                "Go agent for Linux/Jetson",
                "CPU, memory, GPU, disk metrics",
                "ROS2 topic & node monitoring",
                "Local ring buffer for context",
                "Incident trigger detection",
              ]}
            />
            <ArchBlock
              icon={<Zap className="w-6 h-6" />}
              title="Backend"
              items={[
                "FastAPI ingestion service",
                "PostgreSQL for incidents & metadata",
                "Rules-based analysis engine",
                "Replay bundle generator",
                "REST API for all operations",
              ]}
            />
            <ArchBlock
              icon={<FileSearch className="w-6 h-6" />}
              title="Dashboard"
              items={[
                "Incident correlation timeline",
                "Multi-signal metrics charts",
                "Device & deployment tracking",
                "One-click replay bundle export",
                "AI-assisted root cause cards",
              ]}
            />
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section className="py-24 border-t border-border/40">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="text-3xl font-bold mb-12 text-center">
            Built for real robotics failures
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            <UseCaseCard
              title="Topic Starvation"
              description="Camera topic drops from 30Hz to 2Hz. Watchpoint shows the CPU spike, inference backlog, and degraded motion planner outputs — all correlated on one timeline."
              severity="high"
            />
            <UseCaseCard
              title="Thermal Throttling"
              description="Jetson overheats during outdoor operation. Watchpoint captures the temperature rise, GPU frequency throttling, and inference latency increase that triggered a watchdog timeout."
              severity="critical"
            />
            <UseCaseCard
              title="Version Regression"
              description="New deployment causes more mission aborts. Watchpoint groups incidents by release version, showing higher latency in one node path and a config mismatch."
              severity="medium"
            />
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 border-t border-border/40">
        <div className="max-w-6xl mx-auto px-6 text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to debug faster?</h2>
          <p className="text-muted-foreground max-w-lg mx-auto mb-8">
            Get started with Watchpoint in minutes. One install script, instant
            telemetry, automatic incident detection.
          </p>
          <div className="flex flex-col items-center gap-6">
            <div className="bg-muted rounded-lg px-6 py-3 font-mono text-sm max-w-md w-full text-left">
              <span className="text-muted-foreground">$ </span>
              curl -fsSL https://watchpoint.ai/install.sh | bash
              <br />
              <span className="text-muted-foreground">$ </span>
              watchpoint connect --project my-robot
            </div>
            <Link href="/dashboard" className={cn(buttonVariants({ size: "lg" }), "gap-2")}>
              Explore the Demo
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border/40 py-8">
        <div className="max-w-6xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Activity className="w-4 h-4" />
            Watchpoint — Incident intelligence for robots
          </div>
          <div className="text-xs text-muted-foreground">
            Built for ROS2 and edge AI teams
          </div>
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <Card className="bg-card/50 border-border/40 hover:border-border/80 transition-colors">
      <CardHeader className="pb-3">
        <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center mb-2">
          {icon}
        </div>
        <CardTitle className="text-base">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground leading-relaxed">
          {description}
        </p>
      </CardContent>
    </Card>
  );
}

function ArchBlock({
  icon,
  title,
  items,
}: {
  icon: React.ReactNode;
  title: string;
  items: string[];
}) {
  return (
    <div className="border border-border/40 rounded-xl p-6">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center">
          {icon}
        </div>
        <h3 className="font-semibold">{title}</h3>
      </div>
      <ul className="space-y-2">
        {items.map((item) => (
          <li
            key={item}
            className="text-sm text-muted-foreground flex items-start gap-2"
          >
            <span className="mt-1.5 w-1 h-1 rounded-full bg-current flex-shrink-0" />
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}

function UseCaseCard({
  title,
  description,
  severity,
}: {
  title: string;
  description: string;
  severity: "critical" | "high" | "medium" | "low";
}) {
  const colors = {
    critical: "text-red-500 bg-red-500/10 border-red-500/20",
    high: "text-orange-500 bg-orange-500/10 border-orange-500/20",
    medium: "text-yellow-500 bg-yellow-500/10 border-yellow-500/20",
    low: "text-blue-500 bg-blue-500/10 border-blue-500/20",
  };

  return (
    <Card className="bg-card/50 border-border/40">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base">{title}</CardTitle>
          <span
            className={`text-xs px-2 py-0.5 rounded-full border ${colors[severity]}`}
          >
            {severity}
          </span>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground leading-relaxed">
          {description}
        </p>
      </CardContent>
    </Card>
  );
}
