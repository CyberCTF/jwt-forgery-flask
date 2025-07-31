from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
import json
import os
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'quickinsure-secret-key-2024'

# Configuration JWT vulnérable
app.config['JWT_SECRET_KEY'] = 'secret'  # Secret faible pour la vulnérabilité
app.config['JWT_ALGORITHM'] = 'HS256'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

jwt = JWTManager(app)

def init_db():
    """Initialise la base de données SQLite"""
    conn = sqlite3.connect('quickinsure.db')
    cursor = conn.cursor()
    
    # Table des utilisateurs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table des polices d'assurance
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS policies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            policy_number TEXT UNIQUE NOT NULL,
            policy_type TEXT NOT NULL,
            coverage_amount REAL,
            monthly_premium REAL,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Table des réclamations
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS claims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            policy_id INTEGER,
            claim_type TEXT NOT NULL,
            amount REAL,
            description TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (policy_id) REFERENCES policies (id)
        )
    ''')
    
    # Insérer des données de test
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        # Utilisateur test
        cursor.execute('''
            INSERT INTO users (username, password, role, email) 
            VALUES (?, ?, ?, ?)
        ''', ('john.doe', 'Welcome2024!', 'user', 'john.doe@quickinsure.com'))
        
        # Admin avec mot de passe impossible à deviner
        cursor.execute('''
            INSERT INTO users (username, password, role, email) 
            VALUES (?, ?, ?, ?)
        ''', ('admin', 'xK9#mP2$vL8@nQ4&jR7!hF5*wE3', 'admin', 'admin@quickinsure.com'))
        
        # Polices d'assurance
        cursor.execute('''
            INSERT INTO policies (user_id, policy_number, policy_type, coverage_amount, monthly_premium)
            VALUES (?, ?, ?, ?, ?)
        ''', (1, 'POL-2024-001', 'Health Insurance', 50000.0, 150.0))
        
        cursor.execute('''
            INSERT INTO policies (user_id, policy_number, policy_type, coverage_amount, monthly_premium)
            VALUES (?, ?, ?, ?, ?)
        ''', (1, 'POL-2024-002', 'Dental Insurance', 10000.0, 75.0))
        
        # Réclamations
        cursor.execute('''
            INSERT INTO claims (user_id, policy_id, claim_type, amount, description, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (1, 1, 'Medical Visit', 250.0, 'Annual checkup', 'approved'))
    
    conn.commit()
    conn.close()

def load_metadata():
    """Charge les métadonnées depuis le fichier JSON dans deploy"""
    metadata_path = os.path.join(os.path.dirname(__file__), '..', 'deploy', 'metadata.json')
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "site": {"name": "QuickInsure", "description": "Health Insurance Portal"},
            "navigation": {"main": [], "auth": []},
            "footer": {"links": [], "social": []},
            "challenge": {"title": "Challenge", "description": "Description", "skills": [], "points": 0},
            "cta": {"label": "Start", "link": "/"}
        }

@app.route('/')
def home():
    metadata = load_metadata()
    return render_template('home.html', metadata=metadata)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = sqlite3.connect('quickinsure.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, role FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            # Créer un token JWT avec le rôle de l'utilisateur
            access_token = create_access_token(
                identity=user[1],
                additional_claims={'role': user[2], 'user_id': user[0]}
            )
            session['access_token'] = access_token
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'access_token' not in session:
        return redirect(url_for('login'))
    
    # Vérifier le token JWT
    try:
        from flask_jwt_extended import decode_token
        token_data = decode_token(session['access_token'])
        username = token_data['sub']
        role = token_data['role']
        user_id = token_data['user_id']
    except:
        return redirect(url_for('login'))
    
    # Récupérer les données de l'utilisateur
    conn = sqlite3.connect('quickinsure.db')
    cursor = conn.cursor()
    
    # Polices d'assurance
    cursor.execute('''
        SELECT policy_number, policy_type, coverage_amount, monthly_premium, status 
        FROM policies WHERE user_id = ?
    ''', (user_id,))
    policies = cursor.fetchall()
    
    # Réclamations
    cursor.execute('''
        SELECT c.claim_type, c.amount, c.description, c.status, c.created_at, p.policy_number
        FROM claims c 
        JOIN policies p ON c.policy_id = p.id 
        WHERE c.user_id = ?
    ''', (user_id,))
    claims = cursor.fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', 
                         username=username, 
                         role=role, 
                         policies=policies, 
                         claims=claims)

@app.route('/docs')
def docs():
    if 'access_token' not in session:
        return redirect(url_for('login'))
    
    return render_template('docs.html')

@app.route('/api/metadata')
def api_metadata():
    return jsonify(load_metadata())

@app.route('/api/docs')
def api_docs():
    """Endpoint pour récupérer la documentation API"""
    return jsonify({
        'api_version': 'v1.0',
        'base_url': '/api',
        'endpoints': {
            'authentication': {
                'POST /api/login': 'Authenticate user and get JWT token'
            },
            'user': {
                'GET /api/user/profile': 'Get user profile information',
                'GET /api/user/policies': 'Get user insurance policies',
                'GET /api/user/token': 'Get current user JWT token info'
            },
            'admin': {
                'GET /api/admin/system-config': 'Get system configuration (admin only)',
                'GET /api/admin/user-management': 'Get user management data (admin only)'
            }
        },
        'authentication': 'JWT Bearer token required for protected endpoints',
        'note': 'Admin endpoints require admin role in JWT claims'
    })

@app.route('/api/swagger.json')
def swagger_json():
    """OpenAPI/Swagger specification"""
    return jsonify({
        "openapi": "3.0.0",
        "info": {
            "title": "QuickInsure API",
            "description": "Health Insurance Portal API with JWT Authentication",
            "version": "1.0.0"
        },
        "servers": [
            {
                "url": "http://localhost:3206",
                "description": "Development server"
            }
        ],
        "paths": {
            "/api/login": {
                "post": {
                    "summary": "Authenticate user",
                    "description": "Login with username and password to get JWT token",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "username": {"type": "string"},
                                        "password": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Authentication successful",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "access_token": {"type": "string"},
                                            "role": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/user/profile": {
                "get": {
                    "summary": "Get user profile",
                    "security": [{"bearerAuth": []}],
                    "responses": {
                        "200": {"description": "User profile data"}
                    }
                }
            },
            "/api/user/policies": {
                "get": {
                    "summary": "Get user policies",
                    "security": [{"bearerAuth": []}],
                    "responses": {
                        "200": {"description": "User policies data"}
                    }
                }
            },
            "/api/user/token": {
                "get": {
                    "summary": "Get JWT token info",
                    "security": [{"bearerAuth": []}],
                    "responses": {
                        "200": {"description": "JWT token information"}
                    }
                }
            },
            "/api/admin/system-config": {
                "get": {
                    "summary": "Get system configuration",
                    "description": "Admin only - requires admin role in JWT",
                    "security": [{"bearerAuth": []}],
                    "responses": {
                        "200": {"description": "System configuration data"},
                        "403": {"description": "Access denied - admin role required"}
                    }
                }
            },
            "/api/admin/user-management": {
                "get": {
                    "summary": "Get user management data",
                    "description": "Admin only - requires admin role in JWT",
                    "security": [{"bearerAuth": []}],
                    "responses": {
                        "200": {"description": "User management data"},
                        "403": {"description": "Access denied - admin role required"}
                    }
                }
            }
        },
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            }
        }
    })

# API Endpoints
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    conn = sqlite3.connect('quickinsure.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, role FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        access_token = create_access_token(
            identity=user[1],
            additional_claims={'role': user[2], 'user_id': user[0]}
        )
        return jsonify({'access_token': access_token, 'role': user[2]})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/user/profile')
@jwt_required()
def api_user_profile():
    current_user = get_jwt_identity()
    claims = get_jwt()
    
    conn = sqlite3.connect('quickinsure.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username, email, role FROM users WHERE username = ?', (current_user,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({
            'username': user[0],
            'email': user[1],
            'role': user[2]
        })
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/api/user/policies')
@jwt_required()
def api_user_policies():
    claims = get_jwt()
    user_id = claims.get('user_id')
    
    conn = sqlite3.connect('quickinsure.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT policy_number, policy_type, coverage_amount, monthly_premium, status 
        FROM policies WHERE user_id = ?
    ''', (user_id,))
    policies = cursor.fetchall()
    conn.close()
    
    policies_list = []
    for policy in policies:
        policies_list.append({
            'policy_number': policy[0],
            'policy_type': policy[1],
            'coverage_amount': policy[2],
            'monthly_premium': policy[3],
            'status': policy[4]
        })
    
    return jsonify({'policies': policies_list})

@app.route('/api/user/token')
@jwt_required()
def api_user_token():
    """Endpoint pour récupérer le token JWT de l'utilisateur connecté"""
    current_user = get_jwt_identity()
    claims = get_jwt()
    
    return jsonify({
        'message': 'Your JWT token information',
        'user': current_user,
        'role': claims.get('role'),
        'user_id': claims.get('user_id'),
        'token': request.headers.get('Authorization', '').replace('Bearer ', ''),
        'claims': claims
    })

@app.route('/api/admin/system-config')
@jwt_required()
def api_admin_system_config():
    claims = get_jwt()
    role = claims.get('role')
    
    if role != 'admin':
        return jsonify({'error': 'Access denied. Admin role required.'}), 403
    
    # Données sensibles accessibles uniquement aux admins
    secret_data = {
        'admin_api_key': 'sk_live_quickinsure_admin_2024_xK9mP2vL8nQ4jR7hF5wE3',
        'message': 'Congratulations! You have successfully exploited the JWT vulnerability.',
        'sensitive_info': {
            'total_users': 1250,
            'total_policies': 3420,
            'monthly_revenue': 125000,
            'system_secrets': [
                'database_password: quickinsure_db_2024',
                'api_key: sk_live_quickinsure_12345',
                'admin_email: admin@quickinsure.com'
            ]
        }
    }
    
    return jsonify(secret_data)

@app.route('/api/admin/user-management')
@jwt_required()
def api_admin_user_management():
    claims = get_jwt()
    role = claims.get('role')
    
    if role != 'admin':
        return jsonify({'error': 'Access denied. Admin role required.'}), 403
    
    conn = sqlite3.connect('quickinsure.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username, email, role, created_at FROM users')
    users = cursor.fetchall()
    conn.close()
    
    users_list = []
    for user in users:
        users_list.append({
            'username': user[0],
            'email': user[1],
            'role': user[2],
            'created_at': user[3]
        })
    
    return jsonify({'users': users_list})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=3206) 