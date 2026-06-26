// Sample Prisma ORM queries
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

// Find many users
const users = await prisma.user.findMany({
    where: { active: true }
});

// Find first user
const user = await prisma.user.findFirst({
    where: { email: 'john@example.com' }
});

// Find unique user
const uniqueUser = await prisma.user.findUnique({
    where: { id: 1 }
});

// Create new user
const newUser = await prisma.user.create({
    data: {
        name: 'John Doe',
        email: 'john@example.com'
    }
});

// Create many users
const newUsers = await prisma.user.createMany({
    data: [
        { name: 'John Doe', email: 'john@example.com' },
        { name: 'Jane Doe', email: 'jane@example.com' }
    ]
});

// Update user
const updatedUser = await prisma.user.update({
    where: { id: 1 },
    data: { name: 'Jane Doe' }
});

// Update many users
const updateResult = await prisma.user.updateMany({
    where: { active: false },
    data: { active: true }
});

// Delete user
const deletedUser = await prisma.user.delete({
    where: { id: 1 }
});

// Delete many users
const deleteResult = await prisma.user.deleteMany({
    where: { active: false }
});

// Count users
const count = await prisma.user.count({
    where: { active: true }
});

// Aggregate users
const stats = await prisma.user.aggregate({
    where: { active: true },
    _count: true,
    _avg: { age: true },
    _max: { age: true },
    _min: { age: true },
    _sum: { age: true }
});

// Group by
const grouped = await prisma.user.groupBy({
    by: ['role'],
    where: { active: true },
    _count: true
});

// Upsert user
const upsertedUser = await prisma.user.upsert({
    where: { email: 'john@example.com' },
    update: { name: 'John Doe' },
    create: { name: 'John Doe', email: 'john@example.com' }
});
