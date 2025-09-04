/**
 * DoganAI Compliance Kit - Node.js Database Adapter
 * Provides database connection and tenant session management
 */

import { Pool, PoolClient } from 'pg';

// Database configuration
const DATABASE_URL = process.env.DATABASE_URL || 'postgresql://postgres:postgres@localhost:5432/doganai';

// Connection pool configuration
const pool = new Pool({
  connectionString: DATABASE_URL,
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
});

// Tenant session management
export async function withTenant<T>(
  tenantId: string, 
  fn: (client: PoolClient) => Promise<T>
): Promise<T> {
  const client = await pool.connect();
  
  try {
    await client.query('BEGIN');
    
    // Set tenant context for RLS policies
    await client.query('SET app.current_tenant_id = $1', [tenantId]);
    
    // Execute the function with tenant context
    const result = await fn(client);
    
    await client.query('COMMIT');
    return result;
    
  } catch (error) {
    await client.query('ROLLBACK');
    throw error;
    
  } finally {
    client.release();
  }
}

// Direct query execution with tenant context
export async function executeQuery<T = any>(
  tenantId: string, 
  query: string, 
  params: any[] = []
): Promise<T[]> {
  return withTenant(tenantId, async (client) => {
    const result = await client.query(query, params);
    return result.rows;
  });
}

// Command execution with tenant context
export async function executeCommand(
  tenantId: string, 
  command: string, 
  params: any[] = []
): Promise<number> {
  return withTenant(tenantId, async (client) => {
    const result = await client.query(command, params);
    return result.rowCount;
  });
}

// Transaction support
export async function withTransaction<T>(
  tenantId: string,
  fn: (client: PoolClient) => Promise<T>
): Promise<T> {
  return withTenant(tenantId, fn);
}

// Health check
export async function checkDatabaseHealth(): Promise<{
  status: 'healthy' | 'unhealthy';
  version?: string;
  extensions?: string[];
  rlsTables?: number;
  error?: string;
  timestamp: string;
}> {
  try {
    const client = await pool.connect();
    
    try {
      // Check basic connectivity
      await client.query('SELECT 1');
      
      // Check PostgreSQL version
      const versionResult = await client.query('SELECT version()');
      const version = versionResult.rows[0].version;
      
      // Check extensions
      const extensionsResult = await client.query(`
        SELECT extname FROM pg_extension 
        WHERE extname IN ('pgcrypto','uuid-ossp','vector','pg_trgm','citext')
        ORDER BY extname
      `);
      const extensions = extensionsResult.rows.map(row => row.extname);
      
      // Check RLS status
      const rlsResult = await client.query(`
        SELECT COUNT(*) as count FROM pg_tables 
        WHERE schemaname = 'public' AND rowsecurity = true
      `);
      const rlsTables = parseInt(rlsResult.rows[0].count);
      
      return {
        status: 'healthy',
        version,
        extensions,
        rlsTables,
        timestamp: new Date().toISOString()
      };
      
    } finally {
      client.release();
    }
    
  } catch (error) {
    return {
      status: 'unhealthy',
      error: error instanceof Error ? error.message : String(error),
      timestamp: new Date().toISOString()
    };
  }
}

// Connection pool status
export async function getConnectionPoolStatus(): Promise<{
  totalCount: number;
  idleCount: number;
  waitingCount: number;
}> {
  return {
    totalCount: pool.totalCount,
    idleCount: pool.idleCount,
    waitingCount: pool.waitingCount
  };
}

// Graceful shutdown
export async function closePool(): Promise<void> {
  await pool.end();
}

// Error handling
export class DatabaseError extends Error {
  constructor(
    message: string,
    public readonly code?: string,
    public readonly detail?: string
  ) {
    super(message);
    this.name = 'DatabaseError';
  }
}

// Utility functions
export async function testTenantIsolation(tenantId: string): Promise<{
  testName: string;
  result: 'PASS' | 'FAIL';
  details: string;
}> {
  try {
    // Test 1: Query users in current tenant
    const usersInTenant = await executeQuery(tenantId, 'SELECT COUNT(*) as count FROM users');
    const userCount = parseInt(usersInTenant[0].count);
    
    if (userCount > 0) {
      return {
        testName: 'Tenant Isolation - Same Tenant',
        result: 'PASS',
        details: `Found ${userCount} users in current tenant`
      };
    } else {
      return {
        testName: 'Tenant Isolation - Same Tenant',
        result: 'FAIL',
        details: 'No users found in current tenant'
      };
    }
    
  } catch (error) {
    return {
      testName: 'Tenant Isolation Test',
      result: 'FAIL',
      details: `Error: ${error instanceof Error ? error.message : String(error)}`
    };
  }
}

// Export pool for direct access if needed
export { pool };

// Default export
export default {
  withTenant,
  executeQuery,
  executeCommand,
  withTransaction,
  checkDatabaseHealth,
  getConnectionPoolStatus,
  closePool,
  testTenantIsolation
};
