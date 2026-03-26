"""
认证接口测试
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestRegister:
    """注册接口测试"""

    @pytest.mark.asyncio
    async def test_register_success(self, test_client):
        """测试注册成功"""
        response = await test_client.post('/api/register', json={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123'
        })
        data = await response.get_json()

        assert response.status_code == 201
        assert data['message'] == '注册成功'

    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, test_client, test_user):
        """测试重复用户名注册"""
        response = await test_client.post('/api/register', json={
            'username': 'testuser',  # 已存在的用户名
            'email': 'another@example.com',
            'password': 'password123'
        })
        data = await response.get_json()

        assert response.status_code == 400
        assert 'error' in data

    @pytest.mark.asyncio
    async def test_register_missing_email(self, test_client):
        """测试不提供 email 也能注册"""
        response = await test_client.post('/api/register', json={
            'username': 'noemailuser',
            'password': 'password123'
        })
        data = await response.get_json()

        assert response.status_code == 201
        assert data['message'] == '注册成功'


class TestLogin:
    """登录接口测试"""

    @pytest.mark.asyncio
    async def test_login_success(self, test_client, test_user):
        """测试登录成功"""
        response = await test_client.post('/api/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        data = await response.get_json()

        assert response.status_code == 200
        assert data['message'] == '登录成功'
        assert 'access_token' in data
        assert data['token_type'] == 'Bearer'
        assert data['username'] == 'testuser'

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, test_client, test_user):
        """测试密码错误"""
        response = await test_client.post('/api/login', json={
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        data = await response.get_json()

        assert response.status_code == 401
        assert 'error' in data

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, test_client):
        """测试不存在的用户"""
        response = await test_client.post('/api/login', json={
            'username': 'nonexistent',
            'password': 'password123'
        })
        data = await response.get_json()

        assert response.status_code == 401
        assert 'error' in data


class TestProtectedRoute:
    """受保护路由测试"""

    @pytest.mark.asyncio
    async def test_protected_with_valid_token(self, test_client, auth_headers):
        """测试有效 token 访问受保护路由"""
        response = await test_client.get('/api/protected', headers=auth_headers)
        data = await response.get_json()

        assert response.status_code == 200
        assert 'user_id' in data
        assert 'username' in data

    @pytest.mark.asyncio
    async def test_protected_without_token(self, test_client):
        """测试无 token 访问受保护路由"""
        response = await test_client.get('/api/protected')
        data = await response.get_json()

        assert response.status_code == 401
        assert 'error' in data

    @pytest.mark.asyncio
    async def test_protected_with_invalid_token(self, test_client):
        """测试无效 token 访问受保护路由"""
        response = await test_client.get('/api/protected', headers={
            'Authorization': 'Bearer invalid_token'
        })
        data = await response.get_json()

        assert response.status_code == 401
        assert 'error' in data

    @pytest.mark.asyncio
    async def test_protected_with_expired_token(self, test_client):
        """测试过期 token（模拟）"""
        # 使用明显无效的 token
        response = await test_client.get('/api/protected', headers={
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'
        })
        data = await response.get_json()

        assert response.status_code == 401