// import React, { useState, useEffect } from 'react'; // Supprimé

const GraphInfoPanel = ({ node, onFindPath, allNodes }) => {
    if (!node) {
        return (
            React.createElement('div', {id: "info-panel"},
                React.createElement('h2', null, "Explorateur de Graphe AD"),
                React.createElement('p', null, "Cliquez sur un nœud (personne, ordinateur, groupe) ou une relation (flèche) pour afficher ses détails ici."),
                React.createElement('p', null, "Zoomez/Dézoomez avec la molette. Déplacez le graphe en cliquant et glissant sur le fond."),
                React.createElement('p', null, React.createElement('strong', null, "Les données du graphe sont actuellement FFICTIVES et servent de démonstration.")),
                React.createElement('p', null, "Les actions listées ci-dessous sont des simulations et n'ont pas d'effet réel.")
            )
        );
    }
    // Utilisation de React.useState pour targetNodeForPath au lieu de useState direct
    const [targetNodeForPath, setTargetNodeForPath] = React.useState(""); 

    const computerNodesForSelect = allNodes ? allNodes.filter(n => n.data && n.data.type === 'Computer').map(n => n.data) : [];
    const userNodes = allNodes ? allNodes.filter(n => n.data && n.data.type === 'User' && n.data.id !== node.id).map(n => n.data) : [];
    const groupNodes = allNodes ? allNodes.filter(n => n.data && n.data.type === 'Group' && n.data.id !== node.id).map(n => n.data) : [];

    let relatedInfo = [];
    let exploitActions = [];

    if (node.type === 'User') {
        relatedInfo.push({label: "SID", value: node.properties?.sid || 'N/A'});
        relatedInfo.push({label: "Admin Count", value: node.properties?.adminCount?.toString() || 'false'});
        exploitActions.push({ label: `Kerberoast ${node.label}`, action: () => alert(`[Fictif] Tentative de Kerberoasting sur ${node.label}...`) });
        if (node.properties?.adminCount) {
            exploitActions.push({ label: `DCSync (via ${node.label})`, category: 'Exploitation', action: () => alert(`[Fictif] Tentative de DCSync en utilisant les droits de ${node.label}...`) });
        }
        exploitActions.push({ label: `Pass-the-Ticket (depuis ${node.label})`, category: 'Mouvement Latéral', action: () => alert(`[Fictif] Tentative de Pass-the-Ticket avec un ticket de ${node.label}...`) });
        // Assurer que computerNodes existe et est un tableau avant forEach
        const computerNodes = allNodes ? allNodes.filter(n => n.data && n.data.type === 'Computer' && n.data.id !== node.id).map(n => n.data) : [];
        computerNodes.forEach(cn => {
            exploitActions.push({ label: `Chemin d'Exploit vers ${cn.label}`, category: 'Pathfinding', action: () => onFindPath(cn.id), type: 'path' });
        });
        exploitActions.push({ label: `Vérifier Shadow Credentials pour ${node.label}`, category: 'Persistance', action: () => alert(`[Fictif] Recherche de Shadow Credentials sur ${node.label}...`) });
    } else if (node.type === 'Computer') {
        relatedInfo.push({label: "Operating System", value: node.properties?.operatingSystem || 'N/A'});
        relatedInfo.push({label: "DNS HostName", value: node.properties?.dnsHostName || 'N/A'});
        exploitActions.push({ label: `Scanner ports sur ${node.label}`, category: 'Reconnaissance', action: () => alert(`[Fictif] Scan des ports sur ${node.label}...`) });
        if (node.properties?.isDC) {
            exploitActions.push({ label: `Scan Vulns DC (${node.label})`, category: 'Reconnaissance', action: () => alert(`[Fictif] Scan de vulnérabilités (ZeroLogon, PrintNightmare...) sur DC ${node.label}...`) });
            exploitActions.push({ label: `Récupérer NTDS.dit de ${node.label}`, category: 'Credential Access', action: () => alert(`[Fictif] Tentative de récupération de NTDS.dit depuis ${node.label} (via secretsdump ou vshadow)...`) });
        }
        userNodes.forEach(un => {
            exploitActions.push({ label: `Énumérer sessions de ${un.label} sur ${node.label}`, category: 'Reconnaissance', action: () => alert(`[Fictif] Énumération des sessions de ${un.label} sur ${node.label}...`) });
        });
        exploitActions.push({ label: `Exécuter commande via WMI sur ${node.label}`, category: 'Exécution', action: () => alert(`[Fictif] Tentative d'exécution de commande via WMI sur ${node.label}...`) });
    } else if (node.type === 'Group') {
        relatedInfo.push({label: "Scope", value: node.properties?.scope || 'N/A'});
        exploitActions.push({ label: `Énumérer membres de ${node.label}`, category: 'Reconnaissance', action: () => alert(`[Fictif] Énumération des membres du groupe ${node.label}...`) });
        exploitActions.push({ label: `Ajouter utilisateur à ${node.label} (si droits)`, category: 'Persistance', action: () => alert(`[Fictif] Tentative d'ajout d'un utilisateur au groupe ${node.label}...`) });
    } else if (node.type === 'Relation') {
        relatedInfo.push({label: "Type de Relation", value: node.properties?.type || node.label});
        relatedInfo.push({label: "Source", value: node.source});
        relatedInfo.push({label: "Cible", value: node.target});
        if (node.label === 'AdminTo'){
            exploitActions.push({ label: `Abuser de ${node.label} vers ${node.targetNode?.label || node.target}`, category: 'Exploitation', action: () => alert(`[Fictif] Tentative d'abus de la relation AdminTo de ${node.sourceNode?.label || node.source} vers ${node.targetNode?.label || node.target}...`) });
        }
    }
    
    // Regrouper les actions par catégorie pour un meilleur affichage
    const categorizedActions = exploitActions.reduce((acc, action) => {
        const category = action.category || 'Général';
        if (!acc[category]) acc[category] = [];
        acc[category].push(action);
        return acc;
    }, {});

    return (
        React.createElement('div', {id: "info-panel"},
            React.createElement('h2', null, node.label || node.id, React.createElement('span', {className: "node-type-badge"}, node.type)),
            
            node.properties && Object.keys(node.properties).length > 0 && (
                React.createElement(React.Fragment, null,
                    React.createElement('h3', {className: "info-panel-subtitle"}, "Propriétés de l'élément:"),
                    React.createElement('table', {className: "node-details-table"},
                        React.createElement('tbody', null,
                            Object.entries(node.properties).map(([key, value]) => (
                                React.createElement('tr', {key: key},
                                    React.createElement('th', null, key.replace(/([A-Z_])/g, ' $1').replace(/^./, str => str.toUpperCase())),
                                    React.createElement('td', null, typeof value === 'boolean' ? value.toString() : Array.isArray(value) ? value.join(', ') : String(value))
                                )
                            ))
                        )
                    )
                )
            ),
            relatedInfo.length > 0 && (
                 React.createElement(React.Fragment, null,
                    React.createElement('h3', {className: "info-panel-subtitle"}, "Informations Clés:"),
                    React.createElement('ul', {className: "related-info-list"},
                        relatedInfo.map((info, index) => (
                            React.createElement('li', {key: index}, React.createElement('strong', null, info.label, ":"), " ", info.value)
                        ))
                    )
                )
            ),

            Object.keys(categorizedActions).length > 0 && (
                 React.createElement(React.Fragment, null,
                    React.createElement('h3', {className: "info-panel-subtitle with-margin"}, "Actions / Scénarios (Fictifs):"),
                    Object.entries(categorizedActions).map(([category, actions]) => (
                        React.createElement('div', {key: category, className: "action-category"},
                            React.createElement('h4', null, category),
                            React.createElement('div', {className: "exploit-actions-container"},
                                actions.map((actionItem, index) => (
                                    React.createElement('button', {
                                        key: index,
                                        onClick: actionItem.action, 
                                        title: actionItem.label,
                                        className: `exploit-button ${actionItem.type === 'path' ? 'path-finding' : ''}`
                                    },
                                    actionItem.label.length > 40 ? actionItem.label.substring(0,37)+"...": actionItem.label
                                    )
                                ))
                            )
                        )
                    ))
                 )
            ),
            !Object.keys(categorizedActions).length && React.createElement('p', null, "Aucune action spécifique pour cet élément."),
            
            /* Ajout du sélecteur de cible pour pathfinding ici si le noeud sélectionné est un utilisateur */
            node.type === 'User' && React.createElement('div', { className: 'pathfinding-controls', style: { marginTop: '15px', paddingTop: '10px', borderTop: '1px solid #555'} },
                React.createElement('h5', null, "Recherche de chemin d'exploitation"),
                React.createElement('label', { htmlFor: 'target-node-select-gip' }, "Cible (ordinateur): "),
                React.createElement('select', { 
                    id: 'target-node-select-gip',
                    value: targetNodeForPath, 
                    onChange: e => setTargetNodeForPath(e.target.value), 
                    style: { marginRight: '10px' }
                },
                    React.createElement('option', { value: "" }, "-- Choisir un ordinateur --"),
                    computerNodesForSelect.map(cn => React.createElement('option', { key: cn.id, value: cn.id }, cn.label))
                ),
                React.createElement('button', { 
                    onClick: () => onFindPath(targetNodeForPath), 
                    disabled: !targetNodeForPath 
                }, "Trouver Chemin")
            )
        )
    );
}; 