using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;

namespace DoganAI.Compliance.Dtos
{
    /// <summary>
    /// DTO for analytics dashboard data
    /// </summary>
    public class AnalyticsDashboardDto
    {
        public int TotalCompliantEntities { get; set; }
        public int TotalNonCompliantEntities { get; set; }
        public double CompliancePercentage { get; set; }
        public List<ComplianceMetricDto> Metrics { get; set; } = new List<ComplianceMetricDto>();
        public DateTime LastUpdated { get; set; }
    }

    /// <summary>
    /// DTO for individual compliance metrics
    /// </summary>
    public class ComplianceMetricDto
    {
        public string MetricName { get; set; }
        public double Value { get; set; }
        public string Unit { get; set; }
        public string Category { get; set; }
        public DateTime MeasuredAt { get; set; }
    }

    /// <summary>
    /// DTO for compliance report generation request
    /// </summary>
    public class ComplianceReportRequestDto
    {
        [Required]
        public string ReportType { get; set; }
        
        [Required]
        public DateTime StartDate { get; set; }
        
        [Required]
        public DateTime EndDate { get; set; }
        
        public List<string> Entities { get; set; } = new List<string>();
        public List<string> Regulations { get; set; } = new List<string>();
        public string Format { get; set; } = "PDF";
        public bool IncludeCharts { get; set; } = true;
        public bool IncludeRecommendations { get; set; } = true;
    }

    /// <summary>
    /// DTO for compliance report response
    /// </summary>
    public class ComplianceReportDto
    {
        public string ReportId { get; set; }
        public string Title { get; set; }
        public DateTime GeneratedAt { get; set; }
        public string Status { get; set; }
        public ComplianceReportSummaryDto Summary { get; set; }
        public List<ComplianceViolationDto> Violations { get; set; } = new List<ComplianceViolationDto>();
        public List<RecommendationDto> Recommendations { get; set; } = new List<RecommendationDto>();
        public string DownloadUrl { get; set; }
    }

    /// <summary>
    /// DTO for compliance report summary
    /// </summary>
    public class ComplianceReportSummaryDto
    {
        public int TotalEntitiesAudited { get; set; }
        public int CompliantEntities { get; set; }
        public int NonCompliantEntities { get; set; }
        public int CriticalViolations { get; set; }
        public int HighRiskViolations { get; set; }
        public int MediumRiskViolations { get; set; }
        public int LowRiskViolations { get; set; }
        public double OverallComplianceScore { get; set; }
    }

    /// <summary>
    /// DTO for compliance violations
    /// </summary>
    public class ComplianceViolationDto
    {
        public string ViolationId { get; set; }
        public string EntityId { get; set; }
        public string EntityName { get; set; }
        public string RegulationCode { get; set; }
        public string RegulationTitle { get; set; }
        public string ViolationType { get; set; }
        public string Severity { get; set; }
        public string Description { get; set; }
        public DateTime DetectedAt { get; set; }
        public string Status { get; set; }
        public DateTime? ResolvedAt { get; set; }
        public string AssignedTo { get; set; }
    }

    /// <summary>
    /// DTO for compliance recommendations
    /// </summary>
    public class RecommendationDto
    {
        public string RecommendationId { get; set; }
        public string Title { get; set; }
        public string Description { get; set; }
        public string Priority { get; set; }
        public string Category { get; set; }
        public List<string> AffectedEntities { get; set; } = new List<string>();
        public string EstimatedEffort { get; set; }
        public DateTime CreatedAt { get; set; }
    }

    /// <summary>
    /// DTO for audit trail entries
    /// </summary>
    public class AuditTrailDto
    {
        public string AuditId { get; set; }
        public string EntityId { get; set; }
        public string EntityType { get; set; }
        public string Action { get; set; }
        public string UserId { get; set; }
        public string UserName { get; set; }
        public DateTime Timestamp { get; set; }
        public string Details { get; set; }
        public string IpAddress { get; set; }
        public string UserAgent { get; set; }
    }

    /// <summary>
    /// DTO for audit summary request
    /// </summary>
    public class AuditSummaryRequestDto
    {
        [Required]
        public DateTime StartDate { get; set; }
        
        [Required]
        public DateTime EndDate { get; set; }
        
        public string EntityType { get; set; }
        public string UserId { get; set; }
        public List<string> Actions { get; set; } = new List<string>();
    }

    /// <summary>
    /// DTO for audit summary response
    /// </summary>
    public class AuditSummaryDto
    {
        public int TotalActions { get; set; }
        public int UniqueUsers { get; set; }
        public int UniqueEntities { get; set; }
        public Dictionary<string, int> ActionCounts { get; set; } = new Dictionary<string, int>();
        public Dictionary<string, int> UserActionCounts { get; set; } = new Dictionary<string, int>();
        public List<AuditTrailDto> RecentActions { get; set; } = new List<AuditTrailDto>();
        public DateTime GeneratedAt { get; set; }
    }

    /// <summary>
    /// DTO for analytics trend data
    /// </summary>
    public class AnalyticsTrendDto
    {
        public string MetricName { get; set; }
        public List<TrendDataPointDto> DataPoints { get; set; } = new List<TrendDataPointDto>();
        public string TrendDirection { get; set; }
        public double PercentageChange { get; set; }
    }

    /// <summary>
    /// DTO for trend data points
    /// </summary>
    public class TrendDataPointDto
    {
        public DateTime Date { get; set; }
        public double Value { get; set; }
        public string Label { get; set; }
    }

    /// <summary>
    /// DTO for compliance scoring
    /// </summary>
    public class ComplianceScoreDto
    {
        public string EntityId { get; set; }
        public string EntityName { get; set; }
        public double OverallScore { get; set; }
        public Dictionary<string, double> CategoryScores { get; set; } = new Dictionary<string, double>();
        public List<ScoreFactorDto> ScoreFactors { get; set; } = new List<ScoreFactorDto>();
        public DateTime CalculatedAt { get; set; }
    }

    /// <summary>
    /// DTO for score factors
    /// </summary>
    public class ScoreFactorDto
    {
        public string Factor { get; set; }
        public double Weight { get; set; }
        public double Score { get; set; }
        public string Impact { get; set; }
    }
}
