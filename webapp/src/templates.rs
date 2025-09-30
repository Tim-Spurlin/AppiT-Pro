use askama::Template;

/// Dashboard template
#[derive(Template)]
#[template(path = "dashboard.html")]
pub struct Dashboard<'a> {
    pub repositories: &'a Vec<crate::models::Repository>,
    pub stats: &'a crate::models::RepositoryStats,
}

/// Repository overview template
#[derive(Template)]
#[template(path = "repository.html")]
pub struct RepositoryOverview<'a> {
    pub repo: &'a crate::models::Repository,
    pub stats: &'a crate::models::RepositoryStats,
    pub commits: &'a Vec<crate::models::Commit>,
}

/// Commits page template
#[derive(Template)]
#[template(path = "repository.html")] // Reuse repository template for now
pub struct CommitsPage<'a> {
    pub repo: &'a crate::models::Repository,
    pub commits: &'a Vec<crate::models::Commit>,
    pub stats: &'a crate::models::RepositoryStats,
}

/// Graphs page template
#[derive(Template)]
#[template(path = "repository.html")] // Reuse repository template for now
pub struct GraphsPage<'a> {
    pub repo: &'a crate::models::Repository,
    pub stats: &'a crate::models::RepositoryStats,
    pub commits: &'a Vec<crate::models::Commit>,
}

/// Insights page template
#[derive(Template)]
#[template(path = "repository.html")] // Reuse repository template for now
pub struct InsightsPage<'a> {
    pub repo: &'a crate::models::Repository,
    pub stats: &'a crate::models::RepositoryStats,
    pub commits: &'a Vec<crate::models::Commit>,
}