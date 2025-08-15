"""FastAPI application factory."""

from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.config import settings
from app.core.middleware import configure_middleware, get_middleware_info


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        description=settings.api_description,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Configure all middleware using the centralized configuration
    configure_middleware(app)
    
    # Add comprehensive API overview endpoint with HTML response
    @app.get("/", response_class=HTMLResponse)
    async def root():
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>GeoPulse API - Service Overview</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }}
                
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                
                .header {{
                    background: rgba(255, 255, 255, 0.95);
                    backdrop-filter: blur(10px);
                    border-radius: 15px;
                    padding: 30px;
                    margin-bottom: 30px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                    text-align: center;
                }}
                
                .header h1 {{
                    color: #2c3e50;
                    font-size: 2.5em;
                    margin-bottom: 10px;
                    font-weight: 700;
                }}
                
                .header .version {{
                    background: #3498db;
                    color: white;
                    padding: 5px 15px;
                    border-radius: 20px;
                    font-size: 0.9em;
                    display: inline-block;
                    margin-bottom: 15px;
                }}
                
                .header .status {{
                    color: #27ae60;
                    font-size: 1.1em;
                    font-weight: 600;
                }}
                
                .quick-links {{
                    display: flex;
                    gap: 15px;
                    justify-content: center;
                    margin-top: 20px;
                    flex-wrap: wrap;
                }}
                
                .quick-links a {{
                    background: #3498db;
                    color: white;
                    text-decoration: none;
                    padding: 12px 24px;
                    border-radius: 25px;
                    font-weight: 600;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
                }}
                
                .quick-links a:hover {{
                    background: #2980b9;
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(52, 152, 219, 0.4);
                }}
                
                .services-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                    gap: 25px;
                    margin-bottom: 30px;
                }}
                
                .service-card {{
                    background: rgba(255, 255, 255, 0.95);
                    backdrop-filter: blur(10px);
                    border-radius: 15px;
                    padding: 25px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                    transition: transform 0.3s ease;
                }}
                
                .service-card:hover {{
                    transform: translateY(-5px);
                }}
                
                .service-card h3 {{
                    color: #2c3e50;
                    font-size: 1.4em;
                    margin-bottom: 15px;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }}
                
                .service-card .icon {{
                    width: 24px;
                    height: 24px;
                    background: #3498db;
                    border-radius: 50%;
                    display: inline-block;
                }}
                
                .endpoint {{
                    background: #f8f9fa;
                    border-left: 4px solid #3498db;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 0 8px 8px 0;
                }}
                
                .endpoint .method {{
                    font-weight: bold;
                    color: #2c3e50;
                    font-family: 'Courier New', monospace;
                    font-size: 0.9em;
                }}
                
                .endpoint .description {{
                    color: #666;
                    margin: 5px 0;
                    font-size: 0.95em;
                }}
                
                .endpoint .auth {{
                    background: #e74c3c;
                    color: white;
                    padding: 2px 8px;
                    border-radius: 12px;
                    font-size: 0.8em;
                    margin-right: 10px;
                }}
                
                .endpoint .auth.none {{
                    background: #27ae60;
                }}
                
                .features {{
                    background: rgba(255, 255, 255, 0.95);
                    backdrop-filter: blur(10px);
                    border-radius: 15px;
                    padding: 25px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                    margin-bottom: 30px;
                }}
                
                .features h3 {{
                    color: #2c3e50;
                    margin-bottom: 20px;
                    font-size: 1.4em;
                }}
                
                .feature-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                }}
                
                .feature-category {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 10px;
                    border-left: 4px solid #3498db;
                }}
                
                .feature-category h4 {{
                    color: #2c3e50;
                    margin-bottom: 10px;
                    font-size: 1.1em;
                }}
                
                .feature-category ul {{
                    list-style: none;
                }}
                
                .feature-category li {{
                    color: #666;
                    margin: 5px 0;
                    padding-left: 20px;
                    position: relative;
                    font-size: 0.9em;
                }}
                
                .feature-category li:before {{
                    content: "✓";
                    color: #27ae60;
                    font-weight: bold;
                    position: absolute;
                    left: 0;
                }}
                
                .footer {{
                    background: rgba(255, 255, 255, 0.95);
                    backdrop-filter: blur(10px);
                    border-radius: 15px;
                    padding: 20px;
                    text-align: center;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                    color: #666;
                }}
                
                .timestamp {{
                    font-family: 'Courier New', monospace;
                    font-size: 0.9em;
                    color: #999;
                }}
                
                @media (max-width: 768px) {{
                    .container {{
                        padding: 10px;
                    }}
                    
                    .header h1 {{
                        font-size: 2em;
                    }}
                    
                    .services-grid {{
                        grid-template-columns: 1fr;
                    }}
                    
                    .quick-links {{
                        flex-direction: column;
                        align-items: center;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🌍 GeoPulse API</h1>
                    <div class="version">v{settings.api_version}</div>
                    <div class="status">🟢 Service Healthy</div>
                    <p style="margin: 15px 0; color: #666; font-size: 1.1em;">
                        File Upload and Processing API for GeoPulse Platform
                    </p>
                    <div class="quick-links">
                        <a href="/docs">📚 Swagger UI</a>
                        <a href="/redoc">📖 ReDoc</a>
                        <a href="/api/v1/health">🏥 Health Check</a>
                        <a href="/middleware-info">⚙️ System Info</a>
                    </div>
                </div>

                <div class="services-grid">
                    <div class="service-card">
                        <h3><span class="icon" style="background: #e74c3c;"></span> Authentication</h3>
                        <p style="color: #666; margin-bottom: 15px;">User registration and authentication services</p>
                        
                        <div class="endpoint">
                            <div class="method">POST /api/v1/auth/register</div>
                            <div class="description">
                                <span class="auth none">No Auth</span>
                                Register new user with organization details
                            </div>
                        </div>
                        
                        <div class="endpoint">
                            <div class="method">POST /api/v1/auth/login</div>
                            <div class="description">
                                <span class="auth none">No Auth</span>
                                Get JWT access token (30min expiration)
                            </div>
                        </div>
                    </div>

                    <div class="service-card">
                        <h3><span class="icon" style="background: #f39c12;"></span> File Management</h3>
                        <p style="color: #666; margin-bottom: 15px;">File upload, processing, and management services</p>
                        
                        <div class="endpoint">
                            <div class="method">POST /api/v1/files/upload</div>
                            <div class="description">
                                <span class="auth">JWT Required</span>
                                Upload & process XLSX/CSV files (50MB max)
                            </div>
                        </div>
                        
                        <div class="endpoint">
                            <div class="method">GET /api/v1/files/list</div>
                            <div class="description">
                                <span class="auth">JWT Required</span>
                                List user's uploaded files with pagination
                            </div>
                        </div>
                        
                        <div class="endpoint">
                            <div class="method">GET /api/v1/files/status/{{id}}</div>
                            <div class="description">
                                <span class="auth">JWT Required</span>
                                Get file processing status and details
                            </div>
                        </div>
                    </div>

                    <div class="service-card">
                        <h3><span class="icon" style="background: #9b59b6;"></span> Dashboard</h3>
                        <p style="color: #666; margin-bottom: 15px;">User dashboard with analytics and file management</p>
                        
                        <div class="endpoint">
                            <div class="method">GET /api/v1/dashboard</div>
                            <div class="description">
                                <span class="auth">JWT Required</span>
                                Comprehensive dashboard with user profile, file history, and metrics
                            </div>
                        </div>
                    </div>

                    <div class="service-card">
                        <h3><span class="icon" style="background: #27ae60;"></span> Health & Monitoring</h3>
                        <p style="color: #666; margin-bottom: 15px;">System health and monitoring endpoints</p>
                        
                        <div class="endpoint">
                            <div class="method">GET /api/v1/health</div>
                            <div class="description">
                                <span class="auth none">No Auth</span>
                                Basic service health check
                            </div>
                        </div>
                        
                        <div class="endpoint">
                            <div class="method">GET /api/v1/health/detailed</div>
                            <div class="description">
                                <span class="auth none">No Auth</span>
                                Detailed health with database & file system status
                            </div>
                        </div>
                    </div>
                </div>

                <div class="features">
                    <h3>🚀 Platform Features</h3>
                    <div class="feature-grid">
                        <div class="feature-category">
                            <h4>🔐 Security</h4>
                            <ul>
                                <li>JWT authentication (30-min expiration)</li>
                                <li>Bcrypt password hashing</li>
                                <li>Rate limiting (60/min, 1000/hour)</li>
                                <li>CORS protection & security headers</li>
                                <li>Request/response logging</li>
                            </ul>
                        </div>
                        
                        <div class="feature-category">
                            <h4>📁 File Processing</h4>
                            <ul>
                                <li>XLSX, CSV, XLS support</li>
                                <li>File validation & security scanning</li>
                                <li>Core business logic processing</li>
                                <li>Conditional formatting output</li>
                                <li>User-specific storage organization</li>
                            </ul>
                        </div>
                        
                        <div class="feature-category">
                            <h4>💾 Data Storage</h4>
                            <ul>
                                <li>PostgreSQL with async operations</li>
                                <li>JSON file backup storage</li>
                                <li>Connection pooling & transactions</li>
                                <li>File metadata tracking</li>
                                <li>User directory structure</li>
                            </ul>
                        </div>
                        
                        <div class="feature-category">
                            <h4>📊 Monitoring</h4>
                            <ul>
                                <li>Comprehensive logging system</li>
                                <li>Health check endpoints</li>
                                <li>Error tracking & reporting</li>
                                <li>Performance metrics</li>
                                <li>System status monitoring</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="footer">
                    <p><strong>Database:</strong> PostgreSQL with AsyncPG driver | <strong>Tables:</strong> users, files</p>
                    <p><strong>Supported Formats:</strong> .xlsx, .csv, .xls | <strong>Max File Size:</strong> 50MB</p>
                    <p class="timestamp">Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
                </div>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    
    # Add middleware info endpoint for debugging
    @app.get("/middleware-info")
    async def middleware_info():
        return get_middleware_info()
    
    # Include API routes
    from app.api.v1.router import api_router
    app.include_router(api_router, prefix="/api/v1")
    
    return app