use axum::{
    extract::{Path, State},
    http::StatusCode,
    response::{Html, Json},
    routing::get,
    Router,
};
// use serde::{Deserialize, Serialize}; // Commented out unused imports
use std::{collections::HashMap, net::SocketAddr, sync::Arc};
use tokio::signal;
use tower::ServiceBuilder;
use tower_http::{
    cors::CorsLayer,
    services::ServeDir,
    trace::TraceLayer,
};
use tracing::{info, warn, error};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt, EnvFilter};
use askama::Template;

mod analytics;
mod git;
mod models;
mod templates;

use analytics::Analytics;
use models::*;

/// HAASP Insights++ - GitHub-like analytics dashboard
/// 
/// Features:
/// - Repository overview with commit graphs
/// - Code ownership analysis  
/// - Risk scoring and coupling metrics
/// - Performance insights and trends
/// - Local TLS server (127.0.0.1:7420)
#[derive(Clone)]
pub struct AppState {
    analytics: Arc<tokio::sync::RwLock<Analytics>>,
    repositories: Arc<tokio::sync::RwLock<HashMap<String, Repository>>>,
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Initialize tracing
    tracing_subscriber::registry()
        .with(
            EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "haasp_insights=debug,tower_http=debug".into()),
        )
        .with(tracing_subscriber::fmt::layer())
        .init();

    info!("🚀 Starting HAASP Insights++ v1.0.0");

    // Initialize application state
    let analytics = Arc::new(tokio::sync::RwLock::new(Analytics::new()));
    let repositories = Arc::new(tokio::sync::RwLock::new(HashMap::new()));
    
    let state = AppState {
        analytics,
        repositories,
    };

    // Build application router
    let app = Router::new()
        // API routes
        .route("/api/repositories", get(list_repositories))
        .route("/api/repository/:id", get(get_repository))
        .route("/api/repository/:id/commits", get(get_commits))
        .route("/api/repository/:id/analytics", get(get_analytics))
        .route("/api/repository/:id/ownership", get(get_ownership))
        .route("/api/repository/:id/coupling", get(get_coupling))
        .route("/api/repository/:id/risks", get(get_risks))
        
        // Web interface routes
        .route("/", get(dashboard))
        .route("/repo/:id", get(repository_overview))
        .route("/repo/:id/commits", get(commits_page))
        .route("/repo/:id/graphs", get(graphs_page))
        .route("/repo/:id/insights", get(insights_page))
        
        // Static assets
        .nest_service("/static", ServeDir::new("webapp/static"))
        
        .layer(
            ServiceBuilder::new()
                .layer(TraceLayer::new_for_http())
                .layer(CorsLayer::permissive())
        )
        .with_state(state);

    // Setup TLS configuration for local HTTPS
    let _config = setup_tls_config().await?;
    
    // Bind to localhost only for security
    let addr = SocketAddr::from(([127, 0, 0, 1], 7420));
    info!("🔒 HAASP Insights++ listening on https://{}", addr);
    info!("📊 Dashboard available at: https://127.0.0.1:7420");

    // Start server with graceful shutdown
    let listener = tokio::net::TcpListener::bind(addr).await?;
    info!("🎯 Server listening on https://{}", addr);
    
    axum::serve(listener, app.into_make_service())
        .with_graceful_shutdown(shutdown_signal())
        .await?;

    info!("👋 HAASP Insights++ server stopped");
    Ok(())
}

async fn setup_tls_config() -> anyhow::Result<rustls::ServerConfig> {
    use rustls::{Certificate, PrivateKey, ServerConfig};
    use rustls_pemfile::{certs, pkcs8_private_keys};
    use std::io::BufReader;

    // Generate self-signed certificate for local development
    // In production, use proper certificates
    let cert_path = "webapp/cert/localhost.crt";
    let key_path = "webapp/cert/localhost.key";
    
    // Create cert directory if it doesn't exist
    std::fs::create_dir_all("webapp/cert").ok();
    
    // Check if certificates exist, generate if not
    if !std::path::Path::new(cert_path).exists() {
        generate_self_signed_cert(cert_path, key_path)?;
    }

    // Load certificates
    let cert_file = std::fs::File::open(cert_path)?;
    let mut cert_reader = BufReader::new(cert_file);
    let certs = certs(&mut cert_reader)?
        .into_iter()
        .map(Certificate)
        .collect();

    // Load private key
    let key_file = std::fs::File::open(key_path)?;
    let mut key_reader = BufReader::new(key_file);
    let mut keys = pkcs8_private_keys(&mut key_reader)?
        .into_iter()
        .map(PrivateKey)
        .collect::<Vec<_>>();

    if keys.is_empty() {
        return Err(anyhow::anyhow!("No private keys found"));
    }

    let config = ServerConfig::builder()
        .with_safe_defaults()
        .with_no_client_auth()
        .with_single_cert(certs, keys.remove(0))?;

    Ok(config)
}

fn generate_self_signed_cert(cert_path: &str, key_path: &str) -> anyhow::Result<()> {
    info!("🔐 Generating self-signed certificate for localhost");
    
    // Simple certificate generation using openssl command
    // In production, use rcgen crate for pure Rust solution
    let output = std::process::Command::new("openssl")
        .args([
            "req", "-x509", "-newkey", "rsa:4096", "-keyout", key_path,
            "-out", cert_path, "-days", "365", "-nodes", "-subj",
            "/C=US/ST=Local/L=Local/O=HAASP/CN=localhost"
        ])
        .output();

    match output {
        Ok(result) if result.status.success() => {
            info!("✅ Self-signed certificate generated successfully");
            Ok(())
        }
        Ok(result) => {
            error!("❌ Failed to generate certificate: {}", String::from_utf8_lossy(&result.stderr));
            Err(anyhow::anyhow!("Certificate generation failed"))
        }
        Err(_e) => {
            warn!("⚠️  OpenSSL not found, using fallback certificate");
            // Create a basic fallback certificate
            create_fallback_cert(cert_path, key_path)
        }
    }
}

fn create_fallback_cert(cert_path: &str, key_path: &str) -> anyhow::Result<()> {
    // Minimal certificate for development - not secure for production
    let cert_pem = include_str!("../cert/fallback.crt");
    let key_pem = include_str!("../cert/fallback.key");
    
    std::fs::write(cert_path, cert_pem)?;
    std::fs::write(key_path, key_pem)?;
    
    info!("📄 Using fallback certificate (development only)");
    Ok(())
}

// API Handlers

async fn list_repositories(State(state): State<AppState>) -> Json<Vec<Repository>> {
    let repos = state.repositories.read().await;
    let repo_list: Vec<Repository> = repos.values().cloned().collect();
    Json(repo_list)
}

async fn get_repository(
    Path(id): Path<String>, 
    State(state): State<AppState>
) -> Result<Json<Repository>, StatusCode> {
    let repos = state.repositories.read().await;
    match repos.get(&id) {
        Some(repo) => Ok(Json(repo.clone())),
        None => Err(StatusCode::NOT_FOUND),
    }
}

async fn get_commits(
    Path(id): Path<String>, 
    State(state): State<AppState>
) -> Result<Json<Vec<Commit>>, StatusCode> {
    let repos = state.repositories.read().await;
    match repos.get(&id) {
        Some(repo) => {
            // Load commits from git repository
            let commits = state.analytics.read().await.get_commits(&repo.path).await.unwrap_or_default();
            Ok(Json(commits))
        }
        None => Err(StatusCode::NOT_FOUND),
    }
}

async fn get_analytics(
    Path(id): Path<String>, 
    State(state): State<AppState>
) -> Result<Json<RepositoryAnalytics>, StatusCode> {
    let repos = state.repositories.read().await;
    match repos.get(&id) {
        Some(repo) => {
            let analytics = state.analytics.write().await.compute_repository_analytics(&repo.path).await
                .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
            Ok(Json(analytics))
        }
        None => Err(StatusCode::NOT_FOUND),
    }
}

async fn get_ownership(
    Path(id): Path<String>, 
    State(state): State<AppState>
) -> Result<Json<Vec<FileOwnership>>, StatusCode> {
    let repos = state.repositories.read().await;
    match repos.get(&id) {
        Some(repo) => {
            let ownership = state.analytics.read().await.analyze_ownership(&repo.path).await
                .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
            Ok(Json(ownership))
        }
        None => Err(StatusCode::NOT_FOUND),
    }
}

async fn get_coupling(
    Path(id): Path<String>, 
    State(state): State<AppState>
) -> Result<Json<CouplingMatrix>, StatusCode> {
    let repos = state.repositories.read().await;
    match repos.get(&id) {
        Some(repo) => {
            let coupling = state.analytics.read().await.analyze_coupling(&repo.path).await
                .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
            Ok(Json(coupling))
        }
        None => Err(StatusCode::NOT_FOUND),
    }
}

async fn get_risks(
    Path(id): Path<String>, 
    State(state): State<AppState>
) -> Result<Json<Vec<RiskAssessment>>, StatusCode> {
    let repos = state.repositories.read().await;
    match repos.get(&id) {
        Some(repo) => {
            let risks = state.analytics.read().await.assess_risks(&repo.path).await
                .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
            Ok(Json(risks))
        }
        None => Err(StatusCode::NOT_FOUND),
    }
}

// Web Interface Handlers

async fn dashboard(State(state): State<AppState>) -> Html<String> {
    let repos = state.repositories.read().await;
    let repo_list: Vec<Repository> = repos.values().cloned().collect();
    let stats = RepositoryStats { total_commits: 0, branches: 0, files: 0 };
    let dashboard = templates::Dashboard {
        repositories: &repo_list,
        stats: &stats,
    };

    Html(dashboard.render().unwrap_or_else(|_| "Error rendering dashboard".to_string()))
}

async fn repository_overview(
    Path(id): Path<String>, 
    State(state): State<AppState>
) -> Result<Html<String>, StatusCode> {
    let repos = state.repositories.read().await;
    match repos.get(&id) {
        Some(repo) => {
            let stats = state.analytics.write().await.analyze_repository(&repo.path).unwrap_or_default();
            let commits = state.analytics.read().await.get_commits(&repo.path).await.unwrap_or_default();

            let overview = templates::RepositoryOverview {
                repo,
                stats: &stats,
                commits: &commits,
            };

            let html = overview.render()
                .unwrap_or_else(|_| "Error rendering repository overview".to_string());
            Ok(Html(html))
        }
        None => Err(StatusCode::NOT_FOUND),
    }
}

async fn commits_page(
    Path(id): Path<String>, 
    State(state): State<AppState>
) -> Result<Html<String>, StatusCode> {
    let repos = state.repositories.read().await;
    match repos.get(&id) {
        Some(repo) => {
            let commits = state.analytics.read().await.get_commits(&repo.path).await.unwrap_or_default();
            let stats = state.analytics.write().await.analyze_repository(&repo.path).unwrap_or_default();

            let commits_page = templates::CommitsPage {
                repo,
                commits: &commits,
                stats: &stats,
            };

            let html = commits_page.render()
                .unwrap_or_else(|_| "Error rendering commits page".to_string());
            Ok(Html(html))
        }
        None => Err(StatusCode::NOT_FOUND),
    }
}

async fn graphs_page(
    Path(id): Path<String>, 
    State(state): State<AppState>
) -> Result<Html<String>, StatusCode> {
    let repos = state.repositories.read().await;
    match repos.get(&id) {
        Some(repo) => {
            let stats = state.analytics.write().await.analyze_repository(&repo.path).unwrap_or_default();
            let commits = state.analytics.read().await.get_commits(&repo.path).await.unwrap_or_default();

            let graphs_page = templates::GraphsPage {
                repo,
                stats: &stats,
                commits: &commits,
            };

            let html = graphs_page.render()
                .unwrap_or_else(|_| "Error rendering graphs page".to_string());
            Ok(Html(html))
        }
        None => Err(StatusCode::NOT_FOUND),
    }
}

async fn insights_page(
    Path(id): Path<String>, 
    State(state): State<AppState>
) -> Result<Html<String>, StatusCode> {
    let repos = state.repositories.read().await;
    match repos.get(&id) {
        Some(repo) => {
            let stats = state.analytics.write().await.analyze_repository(&repo.path).unwrap_or_default();
            let commits = state.analytics.read().await.get_commits(&repo.path).await.unwrap_or_default();

            let insights_page = templates::InsightsPage {
                repo,
                stats: &stats,
                commits: &commits,
            };

            let html = insights_page.render()
                .unwrap_or_else(|_| "Error rendering insights page".to_string());
            Ok(Html(html))
        }
        None => Err(StatusCode::NOT_FOUND),
    }
}

// Graceful shutdown handling
async fn shutdown_signal() {
    let ctrl_c = async {
        signal::ctrl_c()
            .await
            .expect("failed to install Ctrl+C handler");
    };

    #[cfg(unix)]
    let terminate = async {
        signal::unix::signal(signal::unix::SignalKind::terminate())
            .expect("failed to install signal handler")
            .recv()
            .await;
    };

    #[cfg(not(unix))]
    let terminate = std::future::pending::<()>();

    tokio::select! {
        _ = ctrl_c => {
            info!("🛑 Received Ctrl+C, shutting down gracefully");
        }
        _ = terminate => {
            info!("🛑 Received terminate signal, shutting down gracefully");
        }
    }
}