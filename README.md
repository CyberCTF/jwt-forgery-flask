# CTF Lab: JWT Authentication Bypass in Flask Web Application

## Description
In this lab, you'll exploit JWT authentication vulnerabilities in a simulated health insurance portal built with Flask to gain unauthorized admin access and retrieve sensitive information.

## Objectives
- Analyze JWT token structure and identify vulnerabilities
- Exploit weak JWT implementation to forge authentication tokens
- Bypass authentication controls to access restricted admin endpoints
- Retrieve the admin API key as proof of successful exploitation

## Difficulty
Intermediate

## Estimated Time
45-60 minutes

## Prerequisites
- Basic understanding of JWT tokens and web authentication
- Familiarity with HTTP requests and web proxies
- Basic Python knowledge (optional)
- Burp Suite or similar proxy (optional: jwt.io familiarization)

## Skills Learned
- JWT token analysis and manipulation
- Authentication bypass techniques
- Web application security testing
- API endpoint exploitation

## Project Structure
- folder:build
- folder:deploy
- folder:test
- folder:docs
- file:README.md
- file:.gitignore

## Quick Start
**Prerequisites:** Docker and Docker Compose installed.

**Installation:**
Clone the repository. Run `docker-compose -f deploy/docker-compose.yaml up --build` in the lab root directory. Access the vulnerable webapp at http://localhost:3206.

## Demo Credentials
**User Account (for testing):**
- Username: `john.doe`
- Password: `Welcome2024!`

## Issue Tracker
https://github.com/Cyber-Library/issues 