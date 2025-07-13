describe('Authentication API Tests', () => {
  const testUser = {
    username: 'testuser' + Date.now().toString().slice(-4),
    email: 'test' + Date.now().toString().slice(-4) + '@example.com',
    password: 'Password123!'
  };

  it('should register a new user', () => {
    cy.request({
      method: 'POST',
      url: 'http://localhost:8000/api/auth/register',
      body: testUser
    }).then((response) => {
      expect(response.status).to.equal(201);
      expect(response.body).to.have.property('id');
      expect(response.body.username).to.equal(testUser.username);
      expect(response.body.email).to.equal(testUser.email);
      expect(response.body).to.not.have.property('password');
    });
  });

  it('should not register a user with existing email', () => {
    cy.request({
      method: 'POST',
      url: 'http://localhost:8000/api/auth/register',
      body: testUser,
      failOnStatusCode: false
    }).then((response) => {
      expect(response.status).to.equal(400);
      expect(response.body.detail).to.include('邮箱已存在');
    });
  });

  it('should login with valid credentials', () => {
    cy.request({
      method: 'POST',
      url: 'http://localhost:8000/api/auth/token',
      form: true,
      body: {
        username: testUser.email,
        password: testUser.password
      }
    }).then((response) => {
      expect(response.status).to.equal(200);
      expect(response.body).to.have.property('access_token');
      expect(response.body.token_type).to.equal('bearer');
      // 保存令牌供后续测试使用
      cy.wrap(response.body.access_token).as('authToken');
    });
  });

  it('should access protected route with valid token', function() {
    cy.request({
      method: 'GET',
      url: 'http://localhost:8000/api/auth/me',
      headers: {
        Authorization: `Bearer ${this.authToken}`
      }
    }).then((response) => {
      expect(response.status).to.equal(200);
      expect(response.body.username).to.equal(testUser.username);
      expect(response.body.email).to.equal(testUser.email);
    });
  });

  it('should not access protected route with invalid token', () => {
    cy.request({
      method: 'GET',
      url: 'http://localhost:8000/api/auth/me',
      headers: {
        Authorization: 'Bearer invalid_token'
      },
      failOnStatusCode: false
    }).then((response) => {
      expect(response.status).to.equal(401);
    });
  });
});