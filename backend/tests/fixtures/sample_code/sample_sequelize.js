// Sample Sequelize ORM queries
const { Sequelize, Op } = require('sequelize');

// Find all users
const users = await User.findAll({
    where: { active: true }
});

// Find user by ID
const user = await User.findByPk(1);

// Create new user
const newUser = await User.create({
    name: 'John Doe',
    email: 'john@example.com'
});

// Update user
await User.update(
    { name: 'Jane Doe' },
    { where: { id: 1 } }
);

// Delete user
await User.destroy({
    where: { id: 1 }
});

// Count users
const count = await User.count({
    where: { active: true }
});

// Raw SQL query
const results = await sequelize.query(
    'SELECT * FROM users WHERE created_at > :date',
    {
        replacements: { date: '2024-01-01' },
        type: Sequelize.QueryTypes.SELECT
    }
);

// Complex query with operators
const activeUsers = await User.findAll({
    where: {
        [Op.and]: [
            { active: true },
            { createdAt: { [Op.gte]: new Date('2024-01-01') } }
        ]
    }
});
