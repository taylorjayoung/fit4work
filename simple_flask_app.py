#!/usr/bin/env python3
"""
Simple Flask application for the Job Scraper App.

This script creates a simple Flask application that displays a message
indicating that the Job Scraper App is under development.
"""

from flask import Flask, render_template_string

app = Flask(__name__)

# HTML template for the home page
HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job Scraper App</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {
            padding-top: 56px;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .content {
            flex: 1;
        }
        .footer {
            margin-top: auto;
            padding: 20px 0;
            background-color: #f8f9fa;
        }
        .navbar-brand {
            font-weight: bold;
        }
        .card {
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .card-header {
            font-weight: bold;
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top">
        <div class="container">
            <a class="navbar-brand" href="/">Job Scraper App</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link active" href="/">
                            <i class="fas fa-home"></i> Home
                        </a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <div class="container content mt-4">
        <div class="row">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h1 class="h4 mb-0">Job Scraper App</h1>
                    </div>
                    <div class="card-body">
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle"></i> The Job Scraper App is currently under development. Please check back later.
                        </div>
                        
                        <h2 class="h5 mt-4">Features</h2>
                        <ul>
                            <li>Scrape job listings from multiple job sites</li>
                            <li>Store job information in a database</li>
                            <li>Process user resumes</li>
                            <li>Generate tailored application materials</li>
                            <li>Track job applications</li>
                        </ul>
                        
                        <h2 class="h5 mt-4">Development Status</h2>
                        <p>The application is currently being developed. The following components have been implemented:</p>
                        <ul>
                            <li>Database models and setup</li>
                            <li>Job scrapers for multiple sites</li>
                            <li>Resume processing</li>
                            <li>Message generation</li>
                            <li>Web interface templates</li>
                        </ul>
                        
                        <p>We're currently working on resolving some import issues to get the full application running.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer class="footer">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <p>&copy; 2025 Job Scraper App</p>
                </div>
                <div class="col-md-6 text-end">
                    <p>A comprehensive tool for job seekers</p>
                </div>
            </div>
        </div>
    </footer>

    <!-- Bootstrap JS Bundle with Popper -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

@app.route('/')
def index():
    """Render the home page."""
    return render_template_string(HOME_TEMPLATE)

if __name__ == '__main__':
    print("Starting Flask application on http://localhost:8080")
    app.run(host='0.0.0.0', port=8080, debug=True)
