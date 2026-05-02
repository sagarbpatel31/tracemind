"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { format } from "date-fns";
import {
  Activity,
  AlertTriangle,
  ArrowLeft,
  Brain,
  ChevronRight,
  Clock,
  Download,
  HardDrive,
  Layers,
  Lightbulb,
  Package,
  Zap,
} from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Navbar } from "@/components/layout/navbar";
import type { AnalysisResult, EventLog, Incident, MetricPoint } from "@/types";
import { apiFetch, apiUrl } from "@/lib/api-client";

export default function IncidentDetailPage() {
  const params = useParams();
  const incidentId = params.id as string;

  const [incident, setIncident] = useState<Incident | null>(null);
  const [events, setEvents] = useState<EventLog[]>([]);
  const [metrics, setMetrics] = useState<MetricPoint[]>([]);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const [incidentData, eventsData, metricsData] = await Promise.all([
          apiFetch<Incident>(`/incidents/${incidentId}`),
          apiFetch<EventLog[]>(`/incidents/${incidentId}/events`),
          apiFetch<MetricPoint[]>(`/incidents/${incidentId}/metrics`),
        ]);
        setIncident(incidentData);
        setEvents(eventsData);
        setMetrics(metricsData);
        if (incidentData.analysis_json) {
          setAnalysis(incidentData.analysis_json as unknown as AnalysisResult);
        }
      } catch (err) {
        console.error("Failed to load incident:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [incidentId]);

  async function runAnalysis() {
    setAnalyzing(true);
    try {
      const result = await apiFetch<AnalysisResult>(
        `/incidents/${incidentId}/analyze`,
        { method: "POST" }
      );
      setAnalysis(result);
    } catch (err) {
      console.error("Analysis failed:", err);
    } finally {
      setAnalyzing(false);
    }
  }

  async function downloadBundle() {
    try {
      await apiFetch(`/incidents/${incidentId}/replay-bundle`, {
        method: "POST",
      });
      window.open(apiUrl(`/bundles/${incidentId}`), "_blank");
    } catch (err) {
      console.error("Bundle generation failed:", err);
    }
  }

  // Group metrics by name for charts
  const metricsByName: Record<string, Array<{ time: string; value: number }>> =
    {};
  metrics.forEach((m) => {
    if (!metricsByName[m.metric_name]) {
      metricsByName[m.metric_name] = [];
    }
    metricsByName[m.metric_name].push({
      time: format(new Date(m.timestamp), "HH:mm:ss"),
      value: m.value,
    });
  });

  const chartColors = [
    "#f97316",
    "#3b82f6",
    "#22c55e",
    "#ef4444",
    "#a855f7",
    "#eab308",
  ];

  // Build unified chart data
  const timePoints = new Set<string>();
  metrics.forEach((m) => {
    timePoints.add(format(new Date(m.timestamp), "HH:mm:ss"));
  });
  const sortedTimes = Array.from(timePoints).sort();
  const unifiedChartData = sortedTimes.map((time) => {
    const point: Record<string, string | number> = { time };
    Object.entries(metricsByName).forEach(([name, values]) => {
      const match = values.find((v) => v.time === time);
      if (match) point[name] = match.value;
    });
    return point;
  });

  const metricNames = Object.keys(metricsByName);

  const severityColors: Record<string, string> = {
    critical: "bg-red-500/10 text-red-500 border-red-500/20",
    high: "bg-orange-500/10 text-orange-500 border-orange-500/20",
    medium: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
    low: "bg-blue-500/10 text-blue-500 border-blue-500/20",
  };

  const levelColors: Record<string, string> = {
    error: "text-red-500",
    fatal: "text-red-600 font-semibold",
    warn: "text-yellow-500",
    info: "text-blue-400",
    debug: "text-muted-foreground",
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <main className="max-w-7xl mx-auto px-6 py-8">
          <p className="text-muted-foreground">Loading incident...</p>
        </main>
      </div>
    );
  }

  if (!incident) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <main className="max-w-7xl mx-auto px-6 py-8">
          <p className="text-muted-foreground">Incident not found.</p>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 text-sm text-muted-foreground mb-6">
          <Link
            href="/dashboard"
            className="hover:text-foreground transition-colors flex items-center gap-1"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            Dashboard
          </Link>
          <ChevronRight className="w-3.5 h-3.5" />
          <span className="text-foreground">Incident</span>
        </div>

        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-4 mb-8">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-xl font-bold">{incident.title}</h1>
              <Badge
                variant="outline"
                className={severityColors[incident.severity]}
              >
                {incident.severity}
              </Badge>
            </div>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <span className="flex items-center gap-1">
                <HardDrive className="w-3.5 h-3.5" />
                {incident.device_name || "Unknown device"}
              </span>
              <span className="flex items-center gap-1">
                <Package className="w-3.5 h-3.5" />
                {incident.deployment_version || "No deployment"}
              </span>
              <span className="flex items-center gap-1">
                <Clock className="w-3.5 h-3.5" />
                {format(new Date(incident.started_at), "MMM d, yyyy HH:mm:ss")}
              </span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              className="gap-2"
              onClick={runAnalysis}
              disabled={analyzing}
            >
              <Brain className="w-4 h-4" />
              {analyzing ? "Analyzing..." : "Run Analysis"}
            </Button>
            <Button size="sm" className="gap-2" onClick={downloadBundle}>
              <Download className="w-4 h-4" />
              Replay Bundle
            </Button>
          </div>
        </div>

        {/* Analysis Card */}
        {analysis && (
          <Card className="mb-6 border-primary/20 bg-primary/5">
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <Brain className="w-4 h-4" />
                Root Cause Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm mb-4">{analysis.summary}</p>

              {analysis.probable_causes.length > 0 && (
                <div className="mb-4">
                  <h4 className="text-xs font-semibold uppercase text-muted-foreground mb-2">
                    Probable Causes
                  </h4>
                  <div className="space-y-2">
                    {analysis.probable_causes.map((cause, i) => (
                      <div
                        key={i}
                        className="flex items-start gap-3 p-3 rounded-lg bg-background/50 border border-border/40"
                      >
                        <div className="flex items-center gap-2 min-w-[120px]">
                          <AlertTriangle className="w-3.5 h-3.5 text-orange-500" />
                          <span className="text-xs font-mono text-muted-foreground">
                            {Math.round(cause.confidence * 100)}%
                          </span>
                        </div>
                        <div>
                          <div className="text-sm font-medium">
                            {cause.cause}
                          </div>
                          <div className="text-xs text-muted-foreground mt-0.5">
                            {cause.description}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {analysis.evidence.length > 0 && (
                <div className="mb-4">
                  <h4 className="text-xs font-semibold uppercase text-muted-foreground mb-2">
                    Evidence
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {analysis.evidence.map((e, i) => (
                      <div
                        key={i}
                        className="text-xs px-3 py-1.5 rounded-md bg-background/50 border border-border/40"
                      >
                        <span className="font-mono text-muted-foreground">
                          {e.signal}:
                        </span>{" "}
                        {e.description}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {analysis.suggested_steps.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold uppercase text-muted-foreground mb-2">
                    Suggested Next Steps
                  </h4>
                  <ul className="space-y-1">
                    {analysis.suggested_steps.map((step, i) => (
                      <li
                        key={i}
                        className="text-sm text-muted-foreground flex items-start gap-2"
                      >
                        <Lightbulb className="w-3.5 h-3.5 mt-0.5 text-yellow-500 flex-shrink-0" />
                        {step}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Tabs */}
        <Tabs defaultValue="timeline" className="space-y-4">
          <TabsList>
            <TabsTrigger value="timeline" className="gap-2">
              <Activity className="w-3.5 h-3.5" />
              Timeline
            </TabsTrigger>
            <TabsTrigger value="metrics" className="gap-2">
              <Zap className="w-3.5 h-3.5" />
              Metrics
            </TabsTrigger>
            <TabsTrigger value="events" className="gap-2">
              <Layers className="w-3.5 h-3.5" />
              Events ({events.length})
            </TabsTrigger>
          </TabsList>

          {/* Timeline Tab */}
          <TabsContent value="timeline">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">
                  Incident Correlation Timeline
                </CardTitle>
              </CardHeader>
              <CardContent>
                {unifiedChartData.length === 0 ? (
                  <p className="text-sm text-muted-foreground py-8 text-center">
                    No metric data available. Run the seed script to populate demo telemetry.
                  </p>
                ) : (
                  <div className="h-[400px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={unifiedChartData}>
                        <CartesianGrid
                          strokeDasharray="3 3"
                          stroke="hsl(var(--border))"
                        />
                        <XAxis
                          dataKey="time"
                          stroke="hsl(var(--muted-foreground))"
                          fontSize={11}
                          tickLine={false}
                        />
                        <YAxis
                          stroke="hsl(var(--muted-foreground))"
                          fontSize={11}
                          tickLine={false}
                        />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: "hsl(var(--card))",
                            borderColor: "hsl(var(--border))",
                            borderRadius: "8px",
                            fontSize: "12px",
                          }}
                        />
                        <Legend />
                        {metricNames.map((name, i) => (
                          <Line
                            key={name}
                            type="monotone"
                            dataKey={name}
                            stroke={chartColors[i % chartColors.length]}
                            strokeWidth={2}
                            dot={false}
                            connectNulls
                          />
                        ))}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Metrics Tab - Individual charts */}
          <TabsContent value="metrics">
            <div className="grid md:grid-cols-2 gap-4">
              {metricNames.map((name, i) => (
                <Card key={name}>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium">
                      {name}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="h-[200px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={metricsByName[name]}>
                          <CartesianGrid
                            strokeDasharray="3 3"
                            stroke="hsl(var(--border))"
                          />
                          <XAxis
                            dataKey="time"
                            stroke="hsl(var(--muted-foreground))"
                            fontSize={10}
                            tickLine={false}
                          />
                          <YAxis
                            stroke="hsl(var(--muted-foreground))"
                            fontSize={10}
                            tickLine={false}
                          />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: "hsl(var(--card))",
                              borderColor: "hsl(var(--border))",
                              borderRadius: "8px",
                              fontSize: "12px",
                            }}
                          />
                          <Line
                            type="monotone"
                            dataKey="value"
                            stroke={chartColors[i % chartColors.length]}
                            strokeWidth={2}
                            dot={false}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                </Card>
              ))}
              {metricNames.length === 0 && (
                <p className="text-sm text-muted-foreground col-span-2 py-8 text-center">
                  No metrics data available.
                </p>
              )}
            </div>
          </TabsContent>

          {/* Events Tab */}
          <TabsContent value="events">
            <Card>
              <CardContent className="pt-6">
                {events.length === 0 ? (
                  <p className="text-sm text-muted-foreground py-8 text-center">
                    No events recorded for this incident.
                  </p>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-[140px]">Timestamp</TableHead>
                        <TableHead className="w-[70px]">Level</TableHead>
                        <TableHead className="w-[150px]">Source</TableHead>
                        <TableHead>Message</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {events.map((event) => (
                        <TableRow key={event.id}>
                          <TableCell className="font-mono text-xs">
                            {format(
                              new Date(event.timestamp),
                              "HH:mm:ss.SSS"
                            )}
                          </TableCell>
                          <TableCell>
                            <span
                              className={`text-xs font-mono uppercase ${levelColors[event.level] || ""}`}
                            >
                              {event.level}
                            </span>
                          </TableCell>
                          <TableCell className="text-xs text-muted-foreground font-mono">
                            {event.source}
                          </TableCell>
                          <TableCell className="text-sm">
                            {event.message}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
