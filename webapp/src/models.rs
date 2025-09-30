use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
// use std::collections::HashMap; // Commented out unused import

/// Core data models for HAASP Insights++

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Repository {
    pub id: String,
    pub name: String,
    pub path: String,
    pub description: String,
    pub default_branch: String,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
    pub commit_count: i64,
    pub contributor_count: i64,
    pub language: String,
    pub size_bytes: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Commit {
    pub id: String,
    pub short_id: String,
    pub message: String,
    pub summary: String,
    pub author: Author,
    pub committer: Author,
    pub timestamp: DateTime<Utc>,
    pub parent_ids: Vec<String>,
    pub stats: CommitStats,
    pub verified: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Author {
    pub name: String,
    pub email: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct CommitStats {
    pub additions: i32,
    pub deletions: i32,
    pub files_changed: i32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RepositoryAnalytics {
    pub overview: OverviewStats,
    pub commit_activity: CommitActivity,
    pub language_stats: LanguageStats,
    pub contributor_stats: ContributorStats,
    pub health_score: HealthScore,
}

impl Default for RepositoryAnalytics {
    fn default() -> Self {
        Self {
            overview: OverviewStats::default(),
            commit_activity: CommitActivity::default(),
            language_stats: LanguageStats::default(),
            contributor_stats: ContributorStats::default(),
            health_score: HealthScore::default(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OverviewStats {
    pub total_commits: i64,
    pub total_contributors: i64,
    pub total_files: i64,
    pub total_lines: i64,
    pub avg_commit_size: f64,
    pub commit_frequency: f64, // commits per week
    pub most_active_day: String,
    pub most_active_hour: i32,
}

impl Default for OverviewStats {
    fn default() -> Self {
        Self {
            total_commits: 0,
            total_contributors: 0,
            total_files: 0,
            total_lines: 0,
            avg_commit_size: 0.0,
            commit_frequency: 0.0,
            most_active_day: "Monday".to_string(),
            most_active_hour: 14,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CommitActivity {
    pub daily: Vec<ActivityPoint>,
    pub weekly: Vec<ActivityPoint>,
    pub monthly: Vec<ActivityPoint>,
    pub hourly: Vec<i32>, // 24 hours
    pub weekday: Vec<i32>, // 7 days
}

impl Default for CommitActivity {
    fn default() -> Self {
        Self {
            daily: Vec::new(),
            weekly: Vec::new(),
            monthly: Vec::new(),
            hourly: vec![0; 24],
            weekday: vec![0; 7],
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ActivityPoint {
    pub date: String,
    pub count: i32,
    pub additions: i32,
    pub deletions: i32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LanguageStats {
    pub languages: Vec<LanguageInfo>,
    pub total_bytes: i64,
}

impl Default for LanguageStats {
    fn default() -> Self {
        Self {
            languages: Vec::new(),
            total_bytes: 0,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LanguageInfo {
    pub name: String,
    pub bytes: i64,
    pub percentage: f64,
    pub color: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ContributorStats {
    pub contributors: Vec<Contributor>,
    pub top_contributors: Vec<Contributor>,
    pub new_contributors_last_month: i32,
}

impl Default for ContributorStats {
    fn default() -> Self {
        Self {
            contributors: Vec::new(),
            top_contributors: Vec::new(),
            new_contributors_last_month: 0,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Contributor {
    pub name: String,
    pub email: String,
    pub commit_count: i32,
    pub additions: i32,
    pub deletions: i32,
    pub first_commit: DateTime<Utc>,
    pub last_commit: DateTime<Utc>,
    pub avatar_url: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HealthScore {
    pub overall: f64,
    pub factors: HealthFactors,
}

impl Default for HealthScore {
    fn default() -> Self {
        Self {
            overall: 0.0,
            factors: HealthFactors::default(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HealthFactors {
    pub commit_frequency: f64,
    pub contributor_diversity: f64,
    pub code_quality: f64,
    pub test_coverage: f64,
    pub documentation: f64,
    pub security: f64,
}

impl Default for HealthFactors {
    fn default() -> Self {
        Self {
            commit_frequency: 0.0,
            contributor_diversity: 0.0,
            code_quality: 0.0,
            test_coverage: 0.0,
            documentation: 0.0,
            security: 0.0,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FileOwnership {
    pub path: String,
    pub primary_author: String,
    pub primary_percentage: f64,
    pub contributors: Vec<ContributorShare>,
    pub last_modified: DateTime<Utc>,
    pub modification_count: i32,
    pub risk_level: RiskLevel,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ContributorShare {
    pub name: String,
    pub email: String,
    pub percentage: f64,
    pub line_count: i32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CouplingMatrix {
    pub files: Vec<String>,
    pub matrix: Vec<Vec<f64>>,
    pub strongly_coupled: Vec<CouplingPair>,
}

impl Default for CouplingMatrix {
    fn default() -> Self {
        Self {
            files: Vec::new(),
            matrix: Vec::new(),
            strongly_coupled: Vec::new(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CouplingPair {
    pub file_a: String,
    pub file_b: String,
    pub strength: f64,
    pub change_correlation: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RiskAssessment {
    pub file_path: String,
    pub overall_risk: f64,
    pub risk_factors: RiskFactors,
    pub recommendations: Vec<String>,
    pub priority: Priority,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RiskFactors {
    pub complexity: f64,
    pub coupling: f64,
    pub ownership: f64,
    pub change_frequency: f64,
    pub test_coverage: f64,
    pub bug_history: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum RiskLevel {
    Low,
    Medium,
    High,
    Critical,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Priority {
    Low,
    Normal,
    High,
    Urgent,
}

// Template context structures

#[derive(Debug, Serialize)]
pub struct DashboardContext {
    pub repositories: Vec<Repository>,
    pub recent_activity: Vec<ActivitySummary>,
    pub system_health: SystemHealth,
}

#[derive(Debug, Serialize)]
pub struct ActivitySummary {
    pub repository: String,
    pub action: String,
    pub timestamp: DateTime<Utc>,
    pub author: String,
}

#[derive(Debug, Serialize)]
pub struct SystemHealth {
    pub overall_score: f64,
    pub active_repositories: i32,
    pub total_commits_today: i32,
    pub issues_detected: i32,
}

// Chart data structures

#[derive(Debug, Serialize)]
pub struct ChartData {
    pub labels: Vec<String>,
    pub datasets: Vec<Dataset>,
}

#[derive(Debug, Serialize)]
pub struct Dataset {
    pub label: String,
    pub data: Vec<f64>,
    pub background_color: Option<String>,
    pub border_color: Option<String>,
    pub border_width: Option<i32>,
}

// API request/response structures

#[derive(Debug, Deserialize)]
pub struct AnalyticsRequest {
    pub start_date: Option<DateTime<Utc>>,
    pub end_date: Option<DateTime<Utc>>,
    pub include_files: Option<bool>,
    pub include_metrics: Option<bool>,
}

#[derive(Debug, Serialize)]
pub struct ApiResponse<T> {
    pub success: bool,
    pub data: Option<T>,
    pub error: Option<String>,
    pub timestamp: DateTime<Utc>,
}

impl<T> ApiResponse<T> {
    pub fn success(data: T) -> Self {
        Self {
            success: true,
            data: Some(data),
            error: None,
            timestamp: Utc::now(),
        }
    }
    
    pub fn error(message: &str) -> Self {
        Self {
            success: false,
            data: None,
            error: Some(message.to_string()),
            timestamp: Utc::now(),
        }
    }
}

// Utility functions for models

impl Repository {
    pub fn health_indicator(&self) -> &'static str {
        // Simple health indicator based on recent activity
        if self.updated_at > Utc::now() - chrono::Duration::days(7) {
            "healthy"
        } else if self.updated_at > Utc::now() - chrono::Duration::days(30) {
            "warning"  
        } else {
            "stale"
        }
    }
    
    pub fn size_formatted(&self) -> String {
        if self.size_bytes > 1_000_000 {
            format!("{:.1} MB", self.size_bytes as f64 / 1_000_000.0)
        } else if self.size_bytes > 1_000 {
            format!("{:.1} KB", self.size_bytes as f64 / 1_000.0)
        } else {
            format!("{} B", self.size_bytes)
        }
    }
}

impl Commit {
    pub fn is_merge(&self) -> bool {
        self.parent_ids.len() > 1
    }
    
    pub fn short_message(&self) -> String {
        if self.message.len() > 50 {
            format!("{}...", &self.message[..47])
        } else {
            self.message.clone()
        }
    }
}

impl HealthScore {
    pub fn grade(&self) -> &'static str {
        match self.overall {
            score if score >= 0.9 => "A+",
            score if score >= 0.8 => "A",
            score if score >= 0.7 => "B",
            score if score >= 0.6 => "C",
            score if score >= 0.5 => "D",
            _ => "F",
        }
    }

    pub fn color(&self) -> &'static str {
        match self.overall {
            score if score >= 0.8 => "#28a745", // Green
            score if score >= 0.6 => "#ffc107", // Yellow
            score if score >= 0.4 => "#fd7e14", // Orange
            _ => "#dc3545", // Red
        }
    }
}

/// Repository statistics for quick overview
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RepositoryStats {
    pub total_commits: u64,
    pub branches: u32,
    pub files: u32,
}

impl Default for RepositoryStats {
    fn default() -> Self {
        Self {
            total_commits: 0,
            branches: 0,
            files: 0,
        }
    }
}

/// Repository status information
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RepositoryStatus {
    pub untracked: u32,
    pub modified: u32,
    pub staged: u32,
}

impl Default for RepositoryStatus {
    fn default() -> Self {
        Self {
            untracked: 0,
            modified: 0,
            staged: 0,
        }
    }
}