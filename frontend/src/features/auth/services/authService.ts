import axiosInstance from '@/lib/api/axiosInstance';

export const authService = {
  login: async (email: string, password: string) => {
    const response = await axiosInstance.post('/auth/login', { 
      username: email, 
      password 
    });
    return response.data;
  },

  register: async (email: string, password: string, username: string) => {
    const response = await axiosInstance.post('/auth/register', { 
      email, 
      password,
      username 
    });
    return response.data;
  },

  logout: async () => {
    try {
      await axiosInstance.post('/auth/logout');
    } catch (error) {
      // Logout is client-side for JWT, so ignore errors
      console.log('Logout request failed (expected for JWT)');
    }
  },

  refreshToken: async () => {
    const response = await axiosInstance.post('/auth/refresh');
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await axiosInstance.get('/auth/me');
    return response.data;
  },
};
