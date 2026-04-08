package collector

import (
	"math/rand"
	"runtime"
	"time"
)

// SystemMetrics holds a snapshot of system resource usage.
type SystemMetrics struct {
	Timestamp        time.Time `json:"timestamp"`
	CPUUsagePercent  float64   `json:"cpu_usage_percent"`
	MemoryTotalBytes uint64    `json:"memory_total_bytes"`
	MemoryUsedBytes  uint64    `json:"memory_used_bytes"`
	MemoryAvailable  uint64    `json:"memory_available_bytes"`
	DiskTotalBytes   uint64    `json:"disk_total_bytes"`
	DiskUsedBytes    uint64    `json:"disk_used_bytes"`
	DiskFreeBytes    uint64    `json:"disk_free_bytes"`
	NetBytesSent     uint64    `json:"net_bytes_sent"`
	NetBytesRecv     uint64    `json:"net_bytes_recv"`
}

// Collect gathers current system metrics.
// This is a cross-platform stub that returns simulated values.
// A production implementation would read from /proc (Linux) or use
// platform-specific syscalls.
func Collect() SystemMetrics {
	var memStats runtime.MemStats
	runtime.ReadMemStats(&memStats)

	// Use real Go runtime memory stats where possible, simulate the rest.
	totalMem := uint64(16) * 1024 * 1024 * 1024 // assume 16 GB
	usedMem := memStats.Sys
	if usedMem > totalMem {
		usedMem = totalMem / 2
	}

	totalDisk := uint64(500) * 1024 * 1024 * 1024 // assume 500 GB
	usedDisk := uint64(200) * 1024 * 1024 * 1024   // assume 200 GB used

	return SystemMetrics{
		Timestamp:        time.Now().UTC(),
		CPUUsagePercent:  simulateCPU(),
		MemoryTotalBytes: totalMem,
		MemoryUsedBytes:  usedMem,
		MemoryAvailable:  totalMem - usedMem,
		DiskTotalBytes:   totalDisk,
		DiskUsedBytes:    usedDisk,
		DiskFreeBytes:    totalDisk - usedDisk,
		NetBytesSent:     0, // placeholder
		NetBytesRecv:     0, // placeholder
	}
}

// simulateCPU returns a simulated CPU usage percentage that drifts slowly
// to look somewhat realistic for development/testing purposes.
func simulateCPU() float64 {
	base := 15.0
	jitter := rand.Float64() * 10.0 // 0-10% jitter
	return base + jitter
}
