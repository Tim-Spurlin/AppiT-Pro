use crate::models::*;
use git2::Repository;
use std::path::Path;
use anyhow::Result;

/// Git operations wrapper
pub struct GitService;

impl GitService {
    pub fn new() -> Self {
        Self
    }

    /// Clone a repository
    pub fn clone_repository(url: &str, path: &Path) -> Result<Repository> {
        let repo = Repository::clone(url, path)?;
        Ok(repo)
    }

    /// Open an existing repository
    pub fn open_repository(path: &Path) -> Result<Repository> {
        let repo = Repository::open(path)?;
        Ok(repo)
    }

    /// Get repository status
    pub fn get_status(repo: &Repository) -> Result<RepositoryStatus> {
        let statuses = repo.statuses(None)?;
        let mut status = RepositoryStatus::default();

        for entry in statuses.iter() {
            match entry.status() {
                git2::Status::WT_NEW => status.untracked += 1,
                git2::Status::WT_MODIFIED => status.modified += 1,
                git2::Status::INDEX_NEW => status.staged += 1,
                git2::Status::INDEX_MODIFIED => status.staged += 1,
                _ => {}
            }
        }

        Ok(status)
    }

    /// Get recent commits
    pub fn get_recent_commits(repo: &Repository, limit: usize) -> Result<Vec<Commit>> {
        let mut revwalk = repo.revwalk()?;
        revwalk.push_head()?;

        let mut commits = Vec::new();
        for oid in revwalk.take(limit) {
            if let Ok(oid) = oid {
                if let Ok(commit) = repo.find_commit(oid) {
                    let author = commit.author();
                    let committer = commit.committer();

                    commits.push(Commit {
                        id: oid.to_string(),
                        short_id: format!("{:?}", oid).chars().take(7).collect(),
                        message: commit.message().unwrap_or("").to_string(),
                        summary: commit.summary().unwrap_or("").to_string(),
                        author: Author {
                            name: author.name().unwrap_or("").to_string(),
                            email: author.email().unwrap_or("").to_string(),
                        },
                        committer: Author {
                            name: committer.name().unwrap_or("").to_string(),
                            email: committer.email().unwrap_or("").to_string(),
                        },
                        timestamp: chrono::DateTime::from_timestamp(commit.time().seconds(), 0).unwrap_or_else(|| chrono::Utc::now()),
                        parent_ids: commit.parent_ids().map(|oid| oid.to_string()).collect(),
                        stats: CommitStats {
                            additions: 0, // Would need to compute this
                            deletions: 0,
                            files_changed: 0,
                        },
                        verified: false, // Would need to check signatures
                    });
                }
            }
        }

        Ok(commits)
    }
}