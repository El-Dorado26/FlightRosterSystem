INSERT INTO users (email, hashed_password, full_name, role, is_active, created_at)
VALUES 
  ('admin@flight.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIr.Qa1vTy', 'Admin User', 'admin', true, NOW()),
  ('manager@flight.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Manager User', 'manager', true, NOW()),
  ('user@flight.com', '$2b$12$KTJPQQhN7oc3l6mZQGWj6.yPcpYvz0aGQKQKJLJHKxGgXfMJKqL8W', 'Regular User', 'user', true, NOW()),
  ('viewer@flight.com', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Viewer User', 'viewer', true, NOW())
ON CONFLICT (email) DO NOTHING;
