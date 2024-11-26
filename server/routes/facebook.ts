import express from 'express';
import facebookService from '../services/facebook';

const router = express.Router();

// Test endpoint
router.get('/test', async (req, res) => {
  try {
    console.log('Testing Facebook connection...');
    const connectionTest = await facebookService.testConnection();
    res.json(connectionTest);
  } catch (error: any) {
    console.error('Facebook test endpoint error:', error.response?.data || error.message);
    res.status(500).json({ 
      error: 'Failed to test Facebook connection',
      details: error.response?.data || error.message 
    });
  }
});

// Create test user
router.post('/test-users', async (req, res) => {
  try {
    console.log('Creating test user...');
    const testUser = await facebookService.createTestUser(true);
    res.json({
      message: 'Test user created successfully',
      user: testUser
    });
  } catch (error: any) {
    console.error('Error creating test user:', error.response?.data || error.message);
    res.status(500).json({ 
      error: 'Failed to create test user',
      details: error.response?.data || error.message 
    });
  }
});

// Get test users
router.get('/test-users', async (req, res) => {
  try {
    console.log('Getting test users...');
    const testUsers = await facebookService.getTestUsers();
    res.json({
      message: 'Test users retrieved successfully',
      users: testUsers
    });
  } catch (error: any) {
    console.error('Error getting test users:', error.response?.data || error.message);
    res.status(500).json({ 
      error: 'Failed to get test users',
      details: error.response?.data || error.message 
    });
  }
});

// Delete test user
router.delete('/test-users/:userId', async (req, res) => {
  try {
    const { userId } = req.params;
    console.log(`Deleting test user ${userId}...`);
    await facebookService.deleteTestUser(userId);
    res.json({
      message: 'Test user deleted successfully'
    });
  } catch (error: any) {
    console.error('Error deleting test user:', error.response?.data || error.message);
    res.status(500).json({ 
      error: 'Failed to delete test user',
      details: error.response?.data || error.message 
    });
  }
});

router.get('/page/:pageId', async (req, res) => {
  try {
    const { pageId } = req.params;
    const pageInfo = await facebookService.getPageInfo(pageId);
    res.json(pageInfo);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch page info' });
  }
});

router.get('/page/:pageId/posts', async (req, res) => {
  try {
    const { pageId } = req.params;
    const { limit } = req.query;
    const posts = await facebookService.getPagePosts(pageId, Number(limit) || 10);
    res.json(posts);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch page posts' });
  }
});

router.get('/page/:pageId/insights', async (req, res) => {
  try {
    const { pageId } = req.params;
    const { metrics } = req.query;
    
    if (!metrics || typeof metrics !== 'string') {
      return res.status(400).json({ error: 'Metrics parameter is required' });
    }

    const metricsArray = metrics.split(',');
    const insights = await facebookService.getPageInsights(pageId, metricsArray);
    res.json(insights);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch page insights' });
  }
});

export default router;
