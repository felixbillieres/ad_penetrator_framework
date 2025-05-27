// import React from 'react'; // Supprimé

const Header = ({ activeView, setActiveView }) => {
    const navLinks = [
        { id: 'dashboard', label: 'Dashboard' },
        { id: 'agents', label: 'Agents' },
        { id: 'graph', label: 'Graphe AD' }
    ];
    return (
        <header className="app-header">
            <h1>AD Penetrator <span style={{fontSize: '0.6em', color: '#ccc'}}>Web UI</span></h1>
            <nav>
                {navLinks.map(link => (
                    <a 
                        key={link.id}
                        href="#" 
                        className={activeView === link.id ? 'active' : ''}
                        onClick={(e) => { e.preventDefault(); setActiveView(link.id); }}
                    >
                        {link.label}
                    </a>
                ))}
            </nav>
        </header>
    );
};

// export default Header; // Supprimé 