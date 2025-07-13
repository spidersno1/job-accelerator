describe('Smoke Test', () => {
  it('visits the homepage', () => {
    cy.visit('/');
    cy.contains('Job Accelerator').should('be.visible');
  });
});