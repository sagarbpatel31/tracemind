package sender

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"github.com/tracemind/edge-agent/internal/collector"
)

const demoProjectID = "11111111-1111-1111-1111-111111111111"

// Client sends telemetry data to the TraceMind API.
type Client struct {
	apiURL     string
	deviceID   string
	deviceName string
	httpClient *http.Client
}

// NewClient creates a new sender client.
func NewClient(apiURL, deviceID, deviceName string) *Client {
	return &Client{
		apiURL:     apiURL,
		deviceID:   deviceID,
		deviceName: deviceName,
		httpClient: &http.Client{
			Timeout: 10 * time.Second,
		},
	}
}

// RegisterDevice registers this device with the TraceMind API.
func (c *Client) RegisterDevice() error {
	payload := map[string]string{
		"project_id":  demoProjectID,
		"device_name": c.deviceName,
	}
	return c.post("/api/v1/devices/register", payload)
}

// SendMetrics posts a metrics snapshot to the API as a batch.
func (c *Client) SendMetrics(m collector.SystemMetrics) error {
	now := time.Now().UTC().Format(time.RFC3339)
	metrics := []map[string]interface{}{
		{"device_id": c.deviceID, "timestamp": now, "metric_name": "cpu_percent", "value": m.CPUUsagePercent, "unit": "%"},
		{"device_id": c.deviceID, "timestamp": now, "metric_name": "memory_percent", "value": float64(m.MemoryUsedBytes) / float64(m.MemoryTotalBytes+1) * 100, "unit": "%"},
		{"device_id": c.deviceID, "timestamp": now, "metric_name": "disk_used_percent", "value": float64(m.DiskUsedBytes) / float64(m.DiskTotalBytes+1) * 100, "unit": "%"},
	}
	payload := map[string]interface{}{
		"metrics": metrics,
	}
	return c.post("/api/v1/ingest/metrics", payload)
}

// SendLog posts a log entry to the API as a batch.
func (c *Client) SendLog(level, source, message string) error {
	now := time.Now().UTC().Format(time.RFC3339)
	payload := map[string]interface{}{
		"logs": []map[string]interface{}{
			{
				"device_id": c.deviceID,
				"timestamp": now,
				"level":     level,
				"source":    source,
				"message":   message,
			},
		},
	}
	return c.post("/api/v1/ingest/logs", payload)
}

// post marshals payload to JSON and POSTs it to the given path.
func (c *Client) post(path string, payload interface{}) error {
	body, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("marshal payload: %w", err)
	}

	url := c.apiURL + path
	req, err := http.NewRequest(http.MethodPost, url, bytes.NewReader(body))
	if err != nil {
		return fmt.Errorf("create request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("send request to %s: %w", path, err)
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 300 {
		return fmt.Errorf("unexpected status %d from %s", resp.StatusCode, path)
	}
	return nil
}
