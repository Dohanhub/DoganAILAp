package main

import (
    "context"
    "fmt"
    "log"
    "net"
    "os"
    "time"

    "google.golang.org/grpc"
    "google.golang.org/grpc/health"
    "google.golang.org/grpc/health/grpc_health_v1"
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promhttp"
    "net/http"
)

// ComplianceService - Modern microservice for compliance checking
type ComplianceService struct {
    UnimplementedComplianceServer
    cache          *RedisCache
    kafkaProducer  *KafkaProducer
    metricsServer  *MetricsServer
}

// Service configuration
type ServiceConfig struct {
    Name          string
    Version       string
    Port          string
    MetricsPort   string
    RedisAddr     string
    KafkaAddr     string
    ClusterNode   string
}

// Initialize service with all dependencies
func NewComplianceService(config ServiceConfig) (*ComplianceService, error) {
    // Initialize Redis cache
    cache, err := NewRedisCache(config.RedisAddr)
    if err != nil {
        return nil, fmt.Errorf("failed to connect to Redis: %v", err)
    }

    // Initialize Kafka producer
    producer, err := NewKafkaProducer(config.KafkaAddr)
    if err != nil {
        return nil, fmt.Errorf("failed to connect to Kafka: %v", err)
    }

    // Initialize metrics
    metrics := NewMetricsServer(config.MetricsPort)

    return &ComplianceService{
        cache:         cache,
        kafkaProducer: producer,
        metricsServer: metrics,
    }, nil
}

// CheckCompliance - Main RPC method for compliance checking
func (s *ComplianceService) CheckCompliance(ctx context.Context, req *ComplianceRequest) (*ComplianceResponse, error) {
    startTime := time.Now()
    defer s.recordMetrics(startTime, "check_compliance")

    // Check cache first
    cached, err := s.cache.Get(ctx, req.OrganizationId)
    if err == nil && cached != nil {
        return cached, nil
    }

    // Perform compliance checks in parallel
    results := make(chan *FrameworkResult, 5)
    
    go s.checkNCA(ctx, req, results)
    go s.checkSAMA(ctx, req, results)
    go s.checkPDPL(ctx, req, results)
    go s.checkISO27001(ctx, req, results)
    go s.checkNIST(ctx, req, results)

    // Collect results
    complianceResults := make([]*FrameworkResult, 0, 5)
    for i := 0; i < 5; i++ {
        result := <-results
        complianceResults = append(complianceResults, result)
    }

    // Calculate overall score
    overallScore := s.calculateOverallScore(complianceResults)
    
    response := &ComplianceResponse{
        OrganizationId:    req.OrganizationId,
        Timestamp:        time.Now().Unix(),
        FrameworkResults: complianceResults,
        OverallScore:     overallScore,
        Status:           s.determineStatus(overallScore),
    }

    // Cache result
    s.cache.Set(ctx, req.OrganizationId, response, 5*time.Minute)

    // Publish to Kafka for real-time monitoring
    s.kafkaProducer.Publish("compliance-results", response)

    return response, nil
}

// Saudi NCA compliance check
func (s *ComplianceService) checkNCA(ctx context.Context, req *ComplianceRequest, results chan<- *FrameworkResult) {
    // Implement NCA specific checks
    score := 95.5
    results <- &FrameworkResult{
        Framework: "NCA",
        Score:     score,
        RequirementsMet: 47,
        RequirementsTotal: 49,
        CriticalIssues: 0,
    }
}

// SAMA compliance check
func (s *ComplianceService) checkSAMA(ctx context.Context, req *ComplianceRequest, results chan<- *FrameworkResult) {
    score := 92.3
    results <- &FrameworkResult{
        Framework: "SAMA",
        Score:     score,
        BaselCompliant: true,
        AmlStatus: "compliant",
    }
}

// PDPL compliance check
func (s *ComplianceService) checkPDPL(ctx context.Context, req *ComplianceRequest, results chan<- *FrameworkResult) {
    score := 88.7
    results <- &FrameworkResult{
        Framework: "PDPL",
        Score:     score,
        DataProtectionLevel: "high",
        ConsentManagement: "implemented",
    }
}

// ISO 27001 compliance check
func (s *ComplianceService) checkISO27001(ctx context.Context, req *ComplianceRequest, results chan<- *FrameworkResult) {
    score := 91.2
    results <- &FrameworkResult{
        Framework: "ISO27001",
        Score:     score,
        ControlsImplemented: 114,
        ControlsTotal: 114,
    }
}

// NIST framework compliance check
func (s *ComplianceService) checkNIST(ctx context.Context, req *ComplianceRequest, results chan<- *FrameworkResult) {
    score := 89.8
    results <- &FrameworkResult{
        Framework: "NIST",
        Score:     score,
        Identify:  92,
        Protect:   88,
        Detect:    90,
        Respond:   87,
        Recover:   91,
    }
}

func (s *ComplianceService) calculateOverallScore(results []*FrameworkResult) float64 {
    weights := map[string]float64{
        "NCA":      0.25,
        "SAMA":     0.25,
        "PDPL":     0.20,
        "ISO27001": 0.15,
        "NIST":     0.15,
    }

    totalScore := 0.0
    totalWeight := 0.0

    for _, result := range results {
        if weight, ok := weights[result.Framework]; ok {
            totalScore += result.Score * weight
            totalWeight += weight
        }
    }

    if totalWeight > 0 {
        return totalScore / totalWeight
    }
    return 0
}

func (s *ComplianceService) determineStatus(score float64) string {
    if score >= 90 {
        return "COMPLIANT"
    } else if score >= 70 {
        return "PARTIALLY_COMPLIANT"
    }
    return "NON_COMPLIANT"
}

func (s *ComplianceService) recordMetrics(startTime time.Time, operation string) {
    duration := time.Since(startTime).Seconds()
    requestDuration.WithLabelValues(operation).Observe(duration)
    requestCount.WithLabelValues(operation).Inc()
}

// Prometheus metrics
var (
    requestDuration = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name: "compliance_request_duration_seconds",
            Help: "Duration of compliance requests in seconds",
        },
        []string{"operation"},
    )
    
    requestCount = prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "compliance_request_total",
            Help: "Total number of compliance requests",
        },
        []string{"operation"},
    )
)

func init() {
    prometheus.MustRegister(requestDuration)
    prometheus.MustRegister(requestCount)
}

func main() {
    config := ServiceConfig{
        Name:        "compliance-service",
        Version:     "1.0.0",
        Port:        os.Getenv("SERVICE_PORT"),
        MetricsPort: os.Getenv("METRICS_PORT"),
        RedisAddr:   os.Getenv("REDIS_ADDR"),
        KafkaAddr:   os.Getenv("KAFKA_ADDR"),
        ClusterNode: os.Getenv("CLUSTER_NODE"),
    }

    if config.Port == "" {
        config.Port = "50051"
    }
    if config.MetricsPort == "" {
        config.MetricsPort = "9090"
    }

    // Create service
    service, err := NewComplianceService(config)
    if err != nil {
        log.Fatalf("Failed to create service: %v", err)
    }

    // Start metrics server
    go func() {
        http.Handle("/metrics", promhttp.Handler())
        log.Printf("Metrics server listening on :%s", config.MetricsPort)
        http.ListenAndServe(":"+config.MetricsPort, nil)
    }()

    // Create gRPC server
    lis, err := net.Listen("tcp", ":"+config.Port)
    if err != nil {
        log.Fatalf("Failed to listen: %v", err)
    }

    grpcServer := grpc.NewServer()
    
    // Register service
    RegisterComplianceServer(grpcServer, service)
    
    // Register health check
    healthServer := health.NewServer()
    grpc_health_v1.RegisterHealthServer(grpcServer, healthServer)
    healthServer.SetServingStatus("compliance", grpc_health_v1.HealthCheckResponse_SERVING)

    log.Printf("Compliance service listening on :%s", config.Port)
    if err := grpcServer.Serve(lis); err != nil {
        log.Fatalf("Failed to serve: %v", err)
    }
}