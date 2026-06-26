// Sample raw SQL queries

// Template literal with SQL
const query1 = `SELECT * FROM users WHERE id = ?`;

// Single-quoted SQL
const query2 = 'SELECT name, email FROM users WHERE active = true';

// Double-quoted SQL
const query3 = "INSERT INTO users (name, email) VALUES (?, ?)";

// Complex query
const query4 = `
    SELECT u.*, p.title
    FROM users u
    LEFT JOIN posts p ON u.id = p.user_id
    WHERE u.active = true
    ORDER BY u.created_at DESC
    LIMIT 10
`;

// Update query
const query5 = `UPDATE users SET last_login = NOW() WHERE id = ?`;

// Delete query
const query6 = 'DELETE FROM sessions WHERE expires_at < NOW()';

// Query with JOIN
const query7 = `
    SELECT 
        u.id,
        u.name,
        COUNT(p.id) as post_count
    FROM users u
    LEFT JOIN posts p ON u.id = p.user_id
    GROUP BY u.id, u.name
    HAVING COUNT(p.id) > 0
`;

// Subquery
const query8 = `
    SELECT * FROM users
    WHERE id IN (
        SELECT user_id FROM posts
        WHERE created_at > '2024-01-01'
    )
`;

// CTE
const query9 = `
    WITH active_users AS (
        SELECT * FROM users WHERE active = true
    )
    SELECT * FROM active_users
    WHERE created_at > '2024-01-01'
`;
