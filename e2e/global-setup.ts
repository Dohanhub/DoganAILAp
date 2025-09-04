import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting DoganAI E2E Test Setup...');
  
  // Wait for services to be ready
  const maxRetries = 30;
  let retries = 0;
  
  // Check if backend is ready
  while (retries < maxRetries) {
    try {
      const response = await fetch('http://localhost:8000/health');
      if (response.ok) {
        console.log('✅ Backend service is ready');
        break;
      }
    } catch (error) {
      console.log(`⏳ Waiting for backend service... (${retries + 1}/${maxRetries})`);
      await new Promise(resolve => setTimeout(resolve, 2000));
      retries++;
    }
  }
  
  if (retries === maxRetries) {
    throw new Error('❌ Backend service failed to start within timeout');
  }
  
  // Check if frontend is ready
  retries = 0;
  while (retries < maxRetries) {
    try {
      const response = await fetch('http://localhost:3001');
      if (response.ok) {
        console.log('✅ Frontend service is ready');
        break;
      }
    } catch (error) {
      console.log(`⏳ Waiting for frontend service... (${retries + 1}/${maxRetries})`);
      await new Promise(resolve => setTimeout(resolve, 2000));
      retries++;
    }
  }
  
  if (retries === maxRetries) {
    throw new Error('❌ Frontend service failed to start within timeout');
  }
  
  // Initialize test data if needed
  try {
    const browser = await chromium.launch();
    const context = await browser.newContext();
    const page = await context.newPage();
    
    // Create test database tables if they don't exist
    console.log('🔧 Setting up test database...');
    
    // You can add database initialization here if needed
    // For now, we'll assume the database is properly initialized
    
    await browser.close();
    console.log('✅ Test setup completed successfully');
  } catch (error) {
    console.error('❌ Test setup failed:', error);
    throw error;
  }
}

export default globalSetup;
