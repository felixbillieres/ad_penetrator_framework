// import React, { useState, useRef, useEffect, Fragment } from 'react'; // Supprimé
// import cytoscape from 'cytoscape'; // Supprimé, cytoscape est global

const AdGraphView = () => {
    const [selectedElement, setSelectedElement] = React.useState(null);
    const cyRef = React.useRef(null);
    const [graphError, setGraphError] = React.useState(null);

    // Données AD TRÈS simplifiées pour le débogage
    const debugElements = [
        { data: { id: 'dbg_u1', label: 'User Debug', type: 'User' } },
        { data: { id: 'dbg_c1', label: 'Comp Debug', type: 'Computer' } },
        { data: { id: 'dbg_e1', source: 'dbg_u1', target: 'dbg_c1', label: 'ConnectsTo', type: 'Relation' } }
    ];

    React.useEffect(() => {
        console.log("AdGraphView: React.useEffect démarre.");
        const container = document.getElementById('cy-container');
        if (!container) {
            console.error("AdGraphView: Erreur critique - Le conteneur #cy-container est INTROUVABLE.");
            setGraphError("Erreur critique: Le conteneur du graphe est manquant dans le DOM.");
            return;
        }
        console.log("AdGraphView: Conteneur #cy-container trouvé.", container);

        if (!cytoscape) {
            console.error("AdGraphView: Erreur critique - Cytoscape n'est pas chargé.");
            setGraphError("Erreur critique: La librairie Cytoscape n'est pas disponible.");
            return;
        }
        console.log("AdGraphView: Librairie Cytoscape accessible.");

        try {
            const cyInstance = cytoscape({
                container: container,
                elements: debugElements, // Utilisation des données de débogage
                style: [
                    { selector: 'node', style: { 'background-color': '#61dafb', 'label': 'data(label)', 'color': '#000', 'width': '60px', 'height': '60px' } },
                    { selector: 'edge', style: { 'width': 3, 'line-color': '#ccc', 'target-arrow-color': '#ccc', 'target-arrow-shape': 'triangle', 'label': 'data(label)', 'font-size': '8px' } }
                ],
                layout: {
                    name: 'grid', // Layout le plus simple pour le débogage
                    rows: 1
                }
            });
            console.log("AdGraphView: Instance Cytoscape créée.", cyInstance);

            cyInstance.on('tap', 'node, edge', (event) => {
                setSelectedElement(event.target.data());
            });
            cyInstance.on('tap', (event) => {
                if (event.target === cyInstance) { 
                    setSelectedElement(null); 
                }
            });
            
            cyRef.current = cyInstance;
            setGraphError(null); // Réinitialiser l'erreur si succès
            console.log("AdGraphView: Graphe initialisé et écouteurs d'événements attachés.");

            // Gestion du redimensionnement
            const resizeObserver = new ResizeObserver(() => {
                if(cyRef.current && container) {
                    cyRef.current.resize();
                    cyRef.current.fit(null, 30);
                }
            });
            resizeObserver.observe(container);

            return () => {
                console.log("AdGraphView: Nettoyage de useEffect - destruction de l'instance Cytoscape.");
                if(container) resizeObserver.unobserve(container);
                if(cyRef.current) cyRef.current.destroy();
                cyRef.current = null;
            };
        } catch (e) {
            console.error("AdGraphView: ERREUR lors de l'initialisation de Cytoscape:", e);
            setGraphError(`Erreur Cytoscape: ${e.message}`);
        }

    }, []); // Dépendance vide pour exécution unique après le premier rendu

    const findExploitPaths = (targetNodeId) => {
        if (!cyRef.current || !selectedElement || selectedElement.type !== 'User') {
            alert("Sélectionnez un utilisateur source (nœud) pour la recherche de chemin.");
            return;
        }
        const cy = cyRef.current;
        const sourceId = selectedElement.id;
        
        cy.elements().removeClass('path-highlight').deselect();

        const aStar = cy.elements().aStar({ 
            root: `#${sourceId}`, 
            goal: `#${targetNodeId}`,
            weight: edge => {
                if (edge.data('label') === 'AdminTo') return 1;
                if (edge.data('label') === 'MemberOf') return 2;
                if (edge.data('label') === 'HasSession') return 1.5;
                return 3; 
            }
        });

        if (aStar.found) {
            aStar.path.addClass('path-highlight');
            aStar.path.select();
            const pathNodes = aStar.path.nodes().map(n => n.data('label')).join(' -> ');
            const pathEdges = aStar.path.edges().map(e => e.data('label') || 'related').join(', ');
            setTimeout(() => alert(`Chemin trouvé (coût: ${aStar.distance.toFixed(1)}):
Nœuds: ${pathNodes}
Via: ${pathEdges}`), 100);
        } else {
            alert(`Aucun chemin direct trouvé de ${cy.$('#' + sourceId).data('label')} à ${cy.$('#' + targetNodeId).data('label')}`);
        }
    };

    const recenterGraph = () => {
        if(cyRef.current) {
            cyRef.current.animate({
                fit: { eles: cyRef.current.elements(), padding: 50 },
                duration: 500
            });
        }
    };
    
    const exportGraphPNG = () => {
        if(cyRef.current){
            try {
                const png64 = cyRef.current.png({output: 'base64', full:true, scale: 2, bg: '#21252b'});
                const link = document.createElement('a');
                link.href = 'data:image/png;base64,' + png64;
                link.download = 'ad_penetrator_graph_debug.png';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            } catch (e) {
                console.error("Erreur export PNG:", e);
                alert("Erreur lors de l'exportation en PNG.");
            }
        }
    };

    if (graphError) {
        return (
            React.createElement('div', { className: "ad-graph-view-container error-container" },
                React.createElement('h3', null, "Erreur Graphe AD"),
                React.createElement('p', { className: "error-message" }, graphError),
                React.createElement('p', null, "Veuillez vérifier la console du navigateur (F12) pour plus de détails.")
            )
        );
    }

    return (
        React.createElement(React.Fragment, null,
            React.createElement('div', { className: "graph-controls", style: { paddingBottom: '15px', borderBottom: '1px solid #444', marginBottom: '15px', display: 'flex', gap: '10px' } },
                React.createElement('button', { onClick: recenterGraph, title: "Recentrer le graphe" }, "Recentrer Graphe"),
                React.createElement('button', { onClick: exportGraphPNG, title: "Exporter en PNG" }, "Exporter en PNG")
            ),
            React.createElement('div', { className: "ad-graph-view-container" },
                React.createElement('div', { id: "cy-container", style: { flexGrow: 1, minHeight: '500px', border: '1px dashed red' /* Style de débogage */ } }),
                React.createElement(GraphInfoPanel, { 
                    node: selectedElement, 
                    onFindPath: findExploitPaths, 
                    allNodes: cyRef.current ? cyRef.current.nodes().jsons() : debugElements
                })
            )
        )
    );
};

// export default AdGraphView; 