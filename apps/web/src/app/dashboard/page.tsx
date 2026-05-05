"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { format } from "date-fns";
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  Brain,
  CheckCircle,
  HardDrive,
  Radio,
  Server,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Navbar } from "@/components/layout/navbar";
import type { Device, Incident, IncidentListResponse, ProjectSummary } from "@/types";
import { apiFetch } from "@/lib/api-client";

const DEMO_PROJECT_ID = "11111111-1111-1111-1111-111111111111";

/** True when the incident's analysis contains at least one AI-layer rule finding. */
function hasAiRule(incident: Incident): boolean {
  const causes = (incident.analysis_json as { probable_causes?: Array<{ rule_id?: string }> } | null)
    ?.probable_causes;
  return Array.isArray(causes) && causes.some((c) => c.rule_id?.startsWith("AI-"));
}

export default function DashboardPage() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [summary, setSummary] = useState<ProjectSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [devicesData, incidentsData, summaryData] = await Promise.all([
          apiFetch<Device[]>(`/devices/?project_id=${DEMO_PROJECT_ID}`),
          apiFetch<IncidentListResponse>(
            `/incidents/?project_id=${DEMO_PROJECT_ID}&limit=10`
          ),
          apiFetch<ProjectSummary>(
            `/projects/${DEMO_PROJECT_ID}/summary`
          ),
        ]);
        setDevices(devicesData);
        setIncidents(incidentsData.incidents);
        setSummary(summaryData);
      } catch (err) {
        console.error("Failed to load dashboard data:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const severityColors: Record<string, string> = {
    critical: "bg-red-500/10 text-red-500 border-red-500/20",
    high: "bg-orange-500/10 text-orange-500 border-orange-500/20",
    medium: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
    low: "bg-blue-500/10 text-blue-500 border-blue-500/20",
  };

  const statusIcons: Record<string, React.ReactNode> = {
    open: <AlertTriangle className="w-3.5 h-3.5 text-orange-500" />,
    investigating: <Activity className="w-3.5 h-3.5 text-blue-500" />,
    resolved: <CheckCircle className="w-3.5 h-3.5 text-green-500" />,
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold mb-1">Project Dashboard</h1>
          <p className="text-sm text-muted-foreground">
            Demo project — ROS2 Navigation Stack
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <StatCard
            icon={<Server className="w-4 h-4" />}
            label="Total Devices"
            value={summary?.total_devices ?? "—"}
          />
          <StatCard
            icon={<Radio className="w-4 h-4 text-green-500" />}
            label="Online"
            value={summary?.online_devices ?? "—"}
          />
          <StatCard
            icon={<AlertTriangle className="w-4 h-4 text-orange-500" />}
            label="Total Incidents"
            value={summary?.total_incidents ?? "—"}
          />
          <StatCard
            icon={<Brain className="w-4 h-4 text-violet-500" />}
            label="AI Anomalies"
            value={incidents.filter(hasAiRule).length || "—"}
          />
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Devices */}
          <Card className="lg:col-span-1">
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <HardDrive className="w-4 h-4" />
                Devices
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-2">
                  {[1, 2, 3].map((n) => (
                    <div key={n} className="h-14 rounded-lg bg-muted animate-pulse" />
                  ))}
                </div>
              ) : devices.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No devices registered. Run the seed script to populate demo
                  data.
                </p>
              ) : (
                <div className="space-y-3">
                  {devices.map((device) => (
                    <Link
                      key={device.id}
                      href={`/devices/${device.id}`}
                      className="flex items-center justify-between p-3 rounded-lg border border-border/40 hover:border-border/80 transition-colors group"
                    >
                      <div className="flex items-center gap-3">
                        <span
                          className={`w-2 h-2 rounded-full ${
                            device.status === "online"
                              ? "bg-green-500"
                              : device.status === "offline"
                                ? "bg-red-500"
                                : "bg-gray-500"
                          }`}
                        />
                        <div>
                          <div className="text-sm font-medium">
                            {device.device_name}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {device.hardware_model || "Unknown hardware"}
                          </div>
                        </div>
                      </div>
                      <ArrowRight className="w-4 h-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                    </Link>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Incidents */}
          <Card className="lg:col-span-2">
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <AlertTriangle className="w-4 h-4" />
                Recent Incidents
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-2">
                  {[1, 2, 3].map((n) => (
                    <div key={n} className="h-12 rounded-lg bg-muted animate-pulse" />
                  ))}
                </div>
              ) : incidents.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No incidents yet. Run the seed script to populate demo data.
                </p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Incident</TableHead>
                      <TableHead>Severity</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Started</TableHead>
                      <TableHead></TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {incidents.map((incident) => (
                      <TableRow key={incident.id}>
                        <TableCell>
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="font-medium text-sm">
                              {incident.title}
                            </span>
                            {hasAiRule(incident) && (
                              <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-mono font-semibold bg-violet-500/15 text-violet-400 border border-violet-500/25">
                                <Brain className="w-2.5 h-2.5" />
                                AI anomaly
                              </span>
                            )}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {incident.trigger_type || "manual"}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant="outline"
                            className={severityColors[incident.severity]}
                          >
                            {incident.severity}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-1.5 text-sm">
                            {statusIcons[incident.status]}
                            {incident.status}
                          </div>
                        </TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                          {format(
                            new Date(incident.started_at),
                            "MMM d, HH:mm"
                          )}
                        </TableCell>
                        <TableCell>
                          <Link
                            href={`/incidents/${incident.id}`}
                            className={cn(buttonVariants({ variant: "ghost", size: "sm" }))}
                          >
                            View
                          </Link>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}

function StatCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string | number;
}) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center gap-2 text-muted-foreground mb-2">
          {icon}
          <span className="text-xs">{label}</span>
        </div>
        <div className="text-2xl font-bold">{value}</div>
      </CardContent>
    </Card>
  );
}
