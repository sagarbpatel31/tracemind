"use client";

import Link from "next/link";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { Inference } from "@/types/ai_layer";

interface Props {
  inferences: Inference[];
}

/** Convert timestamp_ns to seconds relative to the first inference. */
function toRelSec(ns: number, baseNs: number): string {
  return ((ns - baseNs) / 1e9).toFixed(2);
}

export function InferenceTimeline({ inferences }: Props) {
  if (inferences.length === 0) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-sm text-muted-foreground py-8 text-center">
            No inference data for this incident.{" "}
            <span className="opacity-60">
              Attach the model-collector to your model to capture inferences.
            </span>
          </p>
        </CardContent>
      </Card>
    );
  }

  const baseNs = inferences[0].timestamp_ns;

  const chartData = inferences.map((inf) => ({
    t: toRelSec(inf.timestamp_ns, baseNs),
    confidence: inf.confidence != null ? Math.round(inf.confidence * 100) / 100 : null,
    latency_ms: inf.latency_ms != null ? Math.round(inf.latency_ms * 10) / 10 : null,
  }));

  return (
    <div className="space-y-4">
      {/* Chart */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Confidence &amp; Latency over Time</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[280px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis
                  dataKey="t"
                  stroke="hsl(var(--muted-foreground))"
                  fontSize={11}
                  tickLine={false}
                  label={{
                    value: "seconds",
                    position: "insideBottomRight",
                    offset: -4,
                    fontSize: 10,
                    fill: "hsl(var(--muted-foreground))",
                  }}
                />
                <YAxis
                  yAxisId="conf"
                  domain={[0, 1]}
                  stroke="hsl(var(--muted-foreground))"
                  fontSize={11}
                  tickLine={false}
                  width={40}
                />
                <YAxis
                  yAxisId="lat"
                  orientation="right"
                  stroke="hsl(var(--muted-foreground))"
                  fontSize={11}
                  tickLine={false}
                  width={50}
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
                <Line
                  yAxisId="conf"
                  type="monotone"
                  dataKey="confidence"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={false}
                  connectNulls
                />
                <Line
                  yAxisId="lat"
                  type="monotone"
                  dataKey="latency_ms"
                  stroke="#f97316"
                  strokeWidth={2}
                  dot={false}
                  connectNulls
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Table */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">
            Inference Frames{" "}
            <span className="text-muted-foreground font-normal text-sm">
              ({inferences.length})
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="pl-6 w-[100px]">t (s)</TableHead>
                <TableHead>Layer</TableHead>
                <TableHead className="w-[100px]">Confidence</TableHead>
                <TableHead className="w-[110px]">Latency (ms)</TableHead>
                <TableHead className="w-[110px]">Output mean</TableHead>
                <TableHead className="w-[110px]">Output std</TableHead>
                <TableHead className="w-[60px]" />
              </TableRow>
            </TableHeader>
            <TableBody>
              {inferences.map((inf) => (
                <TableRow key={inf.id} className="hover:bg-muted/30">
                  <TableCell className="pl-6 font-mono text-xs">
                    {toRelSec(inf.timestamp_ns, baseNs)}
                  </TableCell>
                  <TableCell className="font-mono text-xs text-muted-foreground">
                    {inf.layer_name ?? "—"}
                  </TableCell>
                  <TableCell className="font-mono text-xs">
                    {inf.confidence != null ? (
                      <span
                        className={
                          inf.confidence < 0.5
                            ? "text-red-500"
                            : inf.confidence < 0.75
                              ? "text-yellow-500"
                              : "text-green-500"
                        }
                      >
                        {(inf.confidence * 100).toFixed(1)}%
                      </span>
                    ) : (
                      <span className="text-muted-foreground">—</span>
                    )}
                  </TableCell>
                  <TableCell className="font-mono text-xs">
                    {inf.latency_ms != null ? `${inf.latency_ms.toFixed(1)}` : "—"}
                  </TableCell>
                  <TableCell className="font-mono text-xs text-muted-foreground">
                    {inf.output_mean != null ? inf.output_mean.toFixed(4) : "—"}
                  </TableCell>
                  <TableCell className="font-mono text-xs text-muted-foreground">
                    {inf.output_std != null ? inf.output_std.toFixed(4) : "—"}
                  </TableCell>
                  <TableCell>
                    <Link
                      href={`/inferences/${inf.id}`}
                      className="text-xs text-primary hover:underline"
                    >
                      detail →
                    </Link>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
