import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

class FacebookService {
  private accessToken: string;
  private appId: string;
  private appSecret: string;
  private apiVersion: string = 'v18.0';
  private baseUrl: string = 'https://graph.facebook.com';
  private defaultPermissions: string[] = [
    // Page permissions
    'pages_show_list',
    'pages_read_engagement',
    'pages_manage_posts',
    'pages_manage_metadata',
    
    // Basic permissions
    'public_profile',
    'email',
    
    // Content permissions
    'user_posts',
    'user_photos',
    
    // Social permissions
    'user_friends',
    'user_likes',
    
    // Events and groups
    'user_events',
    'groups_access_member_info'
  ];

  constructor() {
    this.accessToken = process.env.FACEBOOK_ACCESS_TOKEN || '';
    this.appId = process.env.FACEBOOK_APP_ID || '';
    this.appSecret = process.env.FACEBOOK_APP_SECRET || '';

    console.log('Facebook Service Initialization:', {
      accessTokenLength: this.accessToken.length,
      hasAppId: !!this.appId,
      hasAppSecret: !!this.appSecret,
      apiVersion: this.apiVersion,
      permissions: this.defaultPermissions.length
    });
  }

  private getApiUrl(endpoint: string): string {
    return `${this.baseUrl}/${this.apiVersion}/${endpoint}`;
  }

  async getAppToken() {
    try {
      const response = await axios.get(`${this.baseUrl}/${this.apiVersion}/oauth/access_token`, {
        params: {
          client_id: this.appId,
          client_secret: this.appSecret,
          grant_type: 'client_credentials'
        }
      });
      return response.data.access_token;
    } catch (error: any) {
      console.error('Error getting app token:', error.response?.data || error.message);
      throw error;
    }
  }

  async testConnection() {
    try {
      // For development mode, test with /me endpoint
      console.log('Testing with access token...');
      const response = await axios.get(this.getApiUrl('me'), {
        params: {
          access_token: this.accessToken,
          fields: 'id,name'
        }
      });
      return {
        status: 'success',
        user: response.data
      };
    } catch (error: any) {
      console.error('Error testing connection:', error.response?.data || error.message);
      throw error;
    }
  }

  async getTestUser() {
    try {
      const response = await axios.get(this.getApiUrl(`${this.appId}/accounts/test-users`), {
        params: {
          access_token: `${this.appId}|${this.appSecret}`,
        }
      });
      return response.data;
    } catch (error: any) {
      console.error('Error getting test users:', error.response?.data || error.message);
      throw error;
    }
  }

  async getPageInfo(pageId: string) {
    try {
      const response = await axios.get(this.getApiUrl(pageId), {
        params: {
          access_token: this.accessToken,
          fields: 'id,name,fan_count,category,picture'
        }
      });
      return response.data;
    } catch (error: any) {
      console.error('Error fetching page info:', error.response?.data || error.message);
      throw error;
    }
  }

  async getPagePosts(pageId: string, limit: number = 10) {
    try {
      const response = await axios.get(this.getApiUrl(`${pageId}/posts`), {
        params: {
          access_token: this.accessToken,
          fields: 'id,message,created_time,attachments',
          limit
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching page posts:', error);
      throw error;
    }
  }

  async getPageInsights(pageId: string, metrics: string[]) {
    try {
      const response = await axios.get(this.getApiUrl(`${pageId}/insights`), {
        params: {
          access_token: this.accessToken,
          metric: metrics.join(','),
          period: 'day'
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching page insights:', error);
      throw error;
    }
  }

  async createTestUser(installed: boolean = true) {
    try {
      const response = await axios.post(this.getApiUrl(`${this.appId}/accounts/test-users`), null, {
        params: {
          access_token: `${this.appId}|${this.appSecret}`,
          installed: installed,
          permissions: this.defaultPermissions.join(',')
        }
      });
      return response.data;
    } catch (error: any) {
      console.error('Error creating test user:', error.response?.data || error.message);
      throw error;
    }
  }

  async getTestUsers() {
    try {
      const response = await axios.get(this.getApiUrl(`${this.appId}/accounts/test-users`), {
        params: {
          access_token: `${this.appId}|${this.appSecret}`,
        }
      });
      return response.data.data;
    } catch (error: any) {
      console.error('Error getting test users:', error.response?.data || error.message);
      throw error;
    }
  }

  async deleteTestUser(userId: string) {
    try {
      const response = await axios.delete(this.getApiUrl(userId), {
        params: {
          access_token: `${this.appId}|${this.appSecret}`
        }
      });
      return response.data;
    } catch (error: any) {
      console.error('Error deleting test user:', error.response?.data || error.message);
      throw error;
    }
  }
}

export default new FacebookService();
