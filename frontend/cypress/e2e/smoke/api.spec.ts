describe('Backend API Connection', () => {
  it('should connect to backend server and receive valid response', () => {
    cy.request('GET', 'http://localhost:8000/health')
      .its('status').should('eq', 200)
      .its('body').should('have.property', 'status', 'ok');
  });
});