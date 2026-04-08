"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { format } from "date-fns";
import {
  Activity,
  AlertTriangle,
  ArrowLeft,
  CheckCircle,
  ChevronRight,
  Clock,
  Cpu,
  HardDrive,
  Package,
  Radio,
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
import type { Device, Incident, IncidentListResponse } from "@/types";
import { apiFetch } from "@/lib/api-client";

export default function DeviceDetailPage() {
  const params = useParams();
  const deviceId = params.id as string;

  const [device, setDevice] = useState<Device | null>(null);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [deviceData, incidentsData] = await Promise.all([
          apiFetch<Device>(`/devices/${deviceId}`),
          apiFetch<IncidentListResponse>(
            `/incidents/?device_id=${deviceId}&limit=20`
          ),
        ]);
        setDevice(deviceData);
        setIncidents(incidentsData.incidents);
      } catch (err) {
        console.error("Failed to load device:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [deviceId]);

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

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <main className="max-w-7xl mx-auto px-6 py-8">
          <p className="text-muted-foreground">Loading device...</p>
        </main>
      </div>
    );
  }

  if (!device) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <main className="max-w-7xl mx-auto px-6 py-8">
          <p className="text-muted-foreground">Device not found.</p>
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
          <span className="text-foreground">Device</span>
        </div>

        {/* Header */}
        <div className="flex items-start justify-between mb-8">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-xl font-bold">{device.device_name}</h1>
              <span
                className={`w-2.5 h-2.5 rounded-full ${
                  device.status === "online"
                    ? "bg-green-500"
                    : device.status === "offline"
                      ? "bg-red-500"
                      : "bg-gray-500"
                }`}
              />
              <span className="text-sm text-muted-foreground capitalize">
                {device.status}
              </span>
            </div>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <span className="flex items-center gap-1">
                <Cpu className="w-3.5 h-3.5" />
                {device.hardware_model || "Unknown hardware"}
              </span>
              <span className="flex items-center gap-1">
                <HardDrive className="w-3.5 h-3.5" />
                {device.os_version || "Unknown OS"}
              </span>
              {device.agent_version && (
                <span className="flex items-center gap-1">
                  <Package className="w-3.5 h-3.5" />
                  Agent {device.agent_version}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Info cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 text-muted-foreground mb-2">
                <Radio className="w-4 h-4" />
                <span className="text-xs">Status</span>
              </div>
              <div className="text-lg font-bold capitalize">{device.status}</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 text-muted-foreground mb-2">
                <Clock className="w-4 h-4" />
                <span className="text-xs">Last Seen</span>
              </div>
              <div className="text-sm font-medium">
                {device.last_seen_at
                  ? format(new Date(device.last_seen_at), "MMM d, HH:mm")
                  : "Never"}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 text-muted-foreground mb-2">
                <Clock className="w-4 h-4" />
                <span className="text-xs">Registered</span>
              </div>
              <div className="text-sm font-medium">
                {format(new Date(device.registered_at), "MMM d, yyyy")}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 text-muted-foreground mb-2">
                <AlertTriangle className="w-4 h-4" />
                <span className="text-xs">Incidents</span>
              </div>
              <div className="text-lg font-bold">{incidents.length}</div>
            </CardContent>
          </Card>
        </div>

        {/* Incidents */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <AlertTriangle className="w-4 h-4" />
              Linked Incidents
            </CardTitle>
          </CardHeader>
          <CardContent>
            {incidents.length === 0 ? (
              <p className="text-sm text-muted-foreground py-4 text-center">
                No incidents recorded for this device.
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
                        <div className="font-medium text-sm">
                          {incident.title}
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
                        {format(new Date(incident.started_at), "MMM d, HH:mm")}
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
      </main>
    </div>
  );
}
