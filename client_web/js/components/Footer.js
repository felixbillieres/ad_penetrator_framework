// import React from 'react'; // Supprimé

const Footer = () => {
    const uiVersion = "0.2.0-beta"; // Version de l'interface
    const operatorName = "Operator_01"; // Simulé pour l'instant

    return (
        <footer className="app-footer">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0 20px' }}>
                <span>UI Version: {uiVersion} | Operator: {operatorName}</span>
                <span>&copy; {new Date().getFullYear()} AD Penetrator Framework.</span>
            </div>
        </footer>
    );
};

// export default Footer; // Supprimé 