use crate::models::*;
use git2::Repository;
use std::collections::HashMap;
use anyhow::Result;
use chrono;

/// Analytics engine for repository insights
pub struct Analytics {
    cache: HashMap<String, RepositoryStats>,
}

impl Analytics {
    pub fn new() -> Self {
        Self {
            cache: HashMap::new(),
        }
    }

    /// Analyze a repository and return statistics
    pub fn analyze_repository(&mut self, path: &str) -> Result<RepositoryStats> {
        if let Some(stats) = self.cache.get(path) {
            return Ok(stats.clone());
        }

        let repo = Repository::open(path)?;
        let stats = self.compute_stats(&repo)?;
        self.cache.insert(path.to_string(), stats.clone());
        Ok(stats)
    }

    /// Get repository commits
    pub async fn get_commits(&self, path: &str) -> Result<Vec<crate::models::Commit>> {
        let repo = git2::Repository::open(path)?;
        let mut commits = Vec::new();
        
        let mut revwalk = repo.revwalk()?;
        revwalk.push_head()?;
        
        // Get the first 10 commits
        for commit_id in revwalk.take(10) {
            if let Ok(oid) = commit_id {
                if let Ok(commit) = repo.find_commit(oid) {
                    let author = commit.author();
                    let committer = commit.committer();
                    commits.push(crate::models::Commit {
                        id: oid.to_string(),
                        short_id: format!("{:8}", oid),
                        message: commit.message().unwrap_or("").to_string(),
                        summary: commit.summary().unwrap_or("").to_string(),
                        author: crate::models::Author {
                            name: author.name().unwrap_or("Unknown").to_string(),
                            email: author.email().unwrap_or("unknown@example.com").to_string(),
                        },
                        committer: crate::models::Author {
                            name: committer.name().unwrap_or("Unknown").to_string(),
                            email: committer.email().unwrap_or("unknown@example.com").to_string(),
                        },
                        timestamp: chrono::DateTime::from_timestamp(commit.time().seconds(), 0)
                            .unwrap_or_default(),
                        parent_ids: commit.parent_ids().map(|oid| oid.to_string()).collect(),
                        stats: crate::models::CommitStats {
                            additions: 0, // TODO: calculate from diff
                            deletions: 0,
                            files_changed: 0,
                        },
                        verified: false, // TODO: check signature
                    });
                }
            }
        }
        
        Ok(commits)
    }

    /// Compute repository analytics
    pub async fn compute_repository_analytics(&mut self, path: &str) -> Result<RepositoryAnalytics> {
        let _stats = self.analyze_repository(path)?;
        // For now, return basic analytics
        Ok(RepositoryAnalytics::default())
    }

    /// Analyze file ownership patterns
    pub async fn analyze_ownership(&self, _path: &str) -> Result<Vec<FileOwnership>> {
        // TODO: Implement actual ownership analysis
        // For now, return empty vector
        Ok(Vec::new())
    }

    /// Analyze code coupling between files
    pub async fn analyze_coupling(&self, _path: &str) -> Result<CouplingMatrix> {
        // TODO: Implement actual coupling analysis
        // For now, return default matrix
        Ok(CouplingMatrix::default())
    }

    /// Assess risks in the codebase
    pub async fn assess_risks(&self, _path: &str) -> Result<Vec<RiskAssessment>> {
        // TODO: Implement actual risk assessment
        // For now, return empty vector
        Ok(Vec::new())
    }

    fn compute_stats(&self, repo: &Repository) -> Result<RepositoryStats> {
        let mut stats = RepositoryStats::default();

        // Count commits
        let mut revwalk = repo.revwalk()?;
        revwalk.push_head()?;
        stats.total_commits = revwalk.count() as u64;

        // Get branches
        let branches = repo.branches(None)?;
        stats.branches = branches.count() as u32;

        // Basic file count
        if let Ok(head) = repo.head() {
            if let Ok(tree) = head.peel_to_tree() {
                stats.files = self.count_files(&repo, &tree);
            }
        }

        Ok(stats)
    }

    fn count_files(&self, repo: &git2::Repository, tree: &git2::Tree) -> u32 {
        let mut count = 0;
        for entry in tree.iter() {
            if entry.kind() == Some(git2::ObjectType::Tree) {
                if let Ok(obj) = entry.to_object(repo) {
                    if let Some(subtree) = obj.as_tree() {
                        count += self.count_files(repo, subtree);
                    }
                }
            } else {
                count += 1;
            }
        }
        count
    }
}