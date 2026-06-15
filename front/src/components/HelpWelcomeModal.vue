<script setup>
defineProps({
    modelValue: {
        type: Boolean,
        required: true,
    },
    mode: {
        type: String,
        required: true,
    },
});

const emit = defineEmits(["close"]);
</script>

<template>
    <div v-if="modelValue" class="modal-overlay" @click.self="emit('close')">
        <div class="modal-window welcome-window">
            <h3>{{ mode === 'welcome' ? 'Bienvenue dans le solveur' : 'Aide' }}</h3>
            <p class="welcome-intro">
                Ce guide vous aide à démarrer : colorier les zones, choisir la taille,
                utiliser les boutons, consulter l'historique et importer une grille par matrice ou photo.
            </p>
            <div class="welcome-section">
                <h4>1. Colorier la grille</h4>
                <p>
                    Choisissez une couleur dans la palette à droite, puis utilisez les cliques pour remplir la grille :
                </p>
                <ul style="margin: 8px 0; padding-left: 20px;">
                    <li><strong>Clique gauche</strong> : peint la case avec la couleur sélectionnée</li>
                    <li><strong>Clique droit</strong> : efface la case</li>
                    <li><strong>Rester enfoncé et glisser</strong> : continue l'action sur plusieurs cases</li>
                </ul>
                <p>
                    Chaque couleur représente une zone. Le sélecteur <strong>Taille</strong> permet de définir
                    la taille de la grille avant de commencer.
                </p>
            </div>
            <div class="welcome-section">
                <h4>2. Historique</h4>
                <p>
                    Chaque grille résolue est sauvegardée dans l'<strong>historique</strong> de votre session.
                    L'historique affiche le nombre de solutions trouvées et les temps d'exécution du TRM et du baseline.
                    Cliquez sur une entrée de l'historique pour visualiser les solutions d'une grille antérieure.
                </p>
            </div>
            <div class="welcome-section">
                <h4>3. Boutons principaux</h4>
                <div class="welcome-buttons">
                    <div class="welcome-action">
                        <button class="guide-btn new-icon-btn" disabled>
                            <i class="ri-add-line"></i>
                        </button>
                        <div>
                            <strong>Nouvelle grille</strong><br />Crée une grille vide pour repartir à zéro.
                        </div>
                    </div>
                    <div class="welcome-action">
                        <button class="guide-btn solve-icon-btn">
                            <i class="ri-check-line"></i>
                        </button>
                        <div>
                            <strong>Résoudre</strong><br />Lance le solveur et compare TRM / baseline.
                        </div>
                    </div>
                    <div class="welcome-action">
                        <button class="guide-btn reset-icon-btn">
                            <i class="ri-refresh-line"></i>
                        </button>
                        <div>
                            <strong>Réinitialiser</strong><br />Vide la grille actuelle sans changer la taille.
                        </div>
                    </div>
                    <div class="welcome-action">
                        <button class="guide-btn random-icon-btn" disabled>
                            <i class="ri-shuffle-line"></i>
                        </button>
                        <div>
                            <strong>Schéma aléatoire</strong><br />Remplit automatiquement la grille avec un motif de zones aléatoire selon la taille sélectionnée.
                        </div>
                    </div>
                    <div class="welcome-action">
                        <button class="guide-btn benchmark-icon-btn" disabled>
                            <i class="ri-bar-chart-line"></i>
                        </button>
                        <div>
                            <strong>Benchmark aléatoire</strong><br />Lance plusieurs résolutions aléatoires pour comparer TRM et Baseline.
                        </div>
                    </div>
                    <div class="welcome-action">
                        <button class="guide-btn import-icon-btn" disabled>
                            <i class="ri-upload-cloud-line"></i>
                        </button>
                        <div>
                            <strong>Importer</strong><br />Ouvre le panneau pour charger une matrice ou une image.
                        </div>
                    </div>
                    <div class="welcome-action">
                        <button class="guide-btn copy-icon-btn" disabled>
                            <i class="ri-file-copy-line"></i>
                        </button>
                        <div>
                            <strong>Copier la matrice</strong><br />Copie la configuration actuelle de la grille au presse-papiers.
                        </div>
                    </div>
                    <div class="welcome-action">
                        <button class="guide-btn download-icon-btn" disabled>
                            <i class="ri-download-line"></i>
                        </button>
                        <div>
                            <strong>Télécharger en image</strong><br />Télécharge la grille actuelle au format PNG pour la partager ou l'importer plus tard.
                        </div>
                    </div>
                    <div class="welcome-action">
                        <button class="guide-btn help-icon-btn">
                            <i class="ri-question-line"></i>
                        </button>
                        <div>
                            <strong>Afficher l'aide</strong><br />Ouvre ce guide pour consulter l'aide.
                        </div>
                    </div>
                </div>
            </div>
            <div class="welcome-section">
                <h4>4. Raccourcis clavier</h4>
                <ul>
                    <li><kbd>Entrée</kbd> ou <kbd>Espace</kbd> — Résoudre (quand la grille est complète)</li>
                    <li><kbd>←</kbd> / <kbd>→</kbd> — Naviguer entre les solutions</li>
                    <li><kbd>Ctrl+Z</kbd> — Annuler le dernier coup de pinceau</li>
                    <li><kbd>Échap</kbd> — Fermer le modal actif</li>
                </ul>
            </div>
            <div class="welcome-section">
                <h4>5. Statistiques</h4>
                <p>
                    L'onglet <strong>Statistiques</strong> affiche un graphique de performance pour la session actuelle.
                    Vous y voyez les temps moyens de TRM et de Baseline par taille de grille, présentés sur une échelle logarithmique.
                </p>
                <ul>
                    <li>Le graphique agrège uniquement les résolutions de la session en cours.</li>
                    <li>Les petites valeurs en microsecondes et les grandes valeurs en secondes sont affichées proportionnellement.</li>
                </ul>
            </div>
            <div class="welcome-section">
                <h4>5. Système d'import</h4>
                <p>
                    Deux modes sont disponibles : <strong>Matrice</strong> et <strong>Image</strong>.
                </p>
                <ul>
                    <li>
                        <strong>Matrice</strong> : collez un tableau carré de nombres comme
                        <code>0 0 1 1</code> ou <code>0,1,-1,2</code>.
                        <em>-1</em> signifie case vide, les autres nombres définissent les zones.
                    </li>
                    <li>
                        <strong>Image</strong> : sélectionnez une photo de la grille.
                        Le backend analyse l'image et en extrait automatiquement la matrice de zones.
                    </li>
                </ul>
            </div>
            <div class="welcome-section">
                <h4>6. Brouillons</h4>
                <p>
                    Chaque nouvelle grille crée un brouillon enregistré en bas de l'écran.
                    Vous pouvez basculer entre plusieurs brouillons comme des onglets,
                    et supprimer ceux dont vous n'avez plus besoin.
                </p>
                <ul>
                    <li>
                        Les brouillons sont visibles dans le panneau en bas, en tant qu'onglets.
                    </li>
                    <li>
                        La grille en cours est automatiquement sauvegardée lorsque vous changez de brouillon.
                    </li>
                    <li>
                        Il y a une limite de <strong>15 brouillons</strong> maximum,
                        les plus anciens sont supprimés au-delà de ce nombre.
                    </li>
                </ul>
            </div>
            <div class="welcome-section">
                <h4>7. Modèles</h4>
                <p>
                    Un <strong>modèle</strong> désigne ici un algorithme de résolution : une stratégie logique
                    que le programme applique pour trouver les placements valides des reines sur la grille.
                    Ce n'est pas un modèle d'intelligence artificielle entraîné, mais un <em>solveur algorithmique</em>
                    — une suite d'instructions qui explore les possibilités et déduit la solution par raisonnement.
                    L'application compare deux modèles à chaque résolution pour vous montrer leurs différences de performance.
                </p>
                <div class="model-cards">
                    <div class="model-card">
                        <div class="model-card-header model-trm">
                            <span class="model-badge">TRM</span>
                            <strong>Tiny Recursive Model</strong>
                        </div>
                        <p>
                            Le TRM est un solveur par <strong>backtracking récursif optimisé</strong> avec plusieurs techniques avancées.
                            Il utilise des <em>bitsets</em> pour des opérations de domaine en O(1), une <strong>vérification d'adjacence en O(1)</strong>
                            (comparaison avec la ligne précédente uniquement), et du <em>forward-checking</em> pour anticiper les impasses.
                            Il explore un espace de recherche drastiquement réduit.
                        </p>
                        <ul>
                            <li>Bitsets (opérations bit-à-bit) pour les colonnes et zones libres</li>
                            <li>Vérification d'adjacence O(1) : uniquement avec la ligne précédente</li>
                            <li>Forward-checking multi-lignes : atteignabilité des zones libres</li>
                            <li>Typiquement <strong>×1.5 à ×2 plus rapide</strong> que le baseline</li>
                        </ul>
                    </div>
                    <div class="model-card">
                        <div class="model-card-header model-baseline">
                            <span class="model-badge">Baseline</span>
                            <strong>Backtracking naïf exhaustif</strong>
                        </div>
                        <p>
                            Le Baseline est un solveur par <strong>backtracking exhaustif sans optimisation</strong>.
                            Il utilise une <strong>vérification d'adjacence en O(n)</strong> (boucle sur toutes les lignes précédentes)
                            et n'emploie aucune technique de pruning ou d'anticipation. Il explore activement un arbre complet
                            avant de découvrir les contradictions.
                        </p>
                        <ul>
                            <li>Vérification d'adjacence O(n) : boucle sur toutes les reines placées</li>
                            <li>Aucune optimisation, aucun forward-checking</li>
                            <li>Trouve toutes les solutions comme le TRM, mais explore davantage d'états</li>
                            <li>Sert de référence pour mesurer le gain des optimisations du TRM</li>
                        </ul>
                    </div>
                </div>
                <p style="margin-top: 10px; font-size: 0.85em; color: var(--text-secondary, #888);">
                    Les deux modèles produisent exactement les mêmes solutions — la différence réside dans le nombre d'états
                    explorés et donc la <em>vitesse d'exécution</em>. Le TRM explore typiquement 20 à 50 % d'états en moins.
                </p>
            </div>
            <div class="welcome-actions">
                <button class="solve-btn" type="button" @click="emit('close')">
                    {{ mode === 'welcome' ? 'J\'ai compris, continuer' : 'Fermer l\'aide' }}
                </button>
            </div>
        </div>
    </div>
</template>

<style scoped>
.modal-overlay {
    position: fixed;
    inset: 0;
    background-color: rgba(0, 0, 0, 0.45);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
    z-index: 999;
}

.modal-window {
    width: min(100%, 700px);
    background: white;
    border-radius: 16px;
    box-shadow: 0 24px 60px rgba(0, 0, 0, 0.2);
    padding: 1.5rem;
    max-height: 90vh;
    overflow-y: auto;
}

.modal-window h3 {
    margin-top: 0;
    margin-bottom: 0.75rem;
}

.welcome-window {
    max-width: 760px;
}

.welcome-intro {
    margin-bottom: 1rem;
    color: #444;
    font-size: 0.98rem;
}

.welcome-section {
    margin-bottom: 1.2rem;
}

.welcome-section h4 {
    margin-bottom: 0.5rem;
    font-size: 1rem;
    color: #111;
}

.welcome-section p,
.welcome-section ul {
    margin: 0;
    color: #444;
    line-height: 1.55;
    font-size: 0.95rem;
}

.welcome-section ul {
    padding-left: 1.2rem;
    margin-top: 0.7rem;
}

.welcome-section li {
    margin-bottom: 0.7rem;
}

.model-cards {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1rem;
    margin-top: 0.8rem;
}

.model-card {
    border: 1px solid #e3e8f0;
    border-radius: 14px;
    overflow: hidden;
    background: #fbfbff;
}

.model-card-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.7rem 1rem;
    font-size: 0.95rem;
}

.model-trm {
    background: linear-gradient(90deg, #e8f0fe 0%, #f0f4ff 100%);
    border-bottom: 1px solid #c5d5f8;
}

.model-baseline {
    background: linear-gradient(90deg, #fef3e8 0%, #fff8f0 100%);
    border-bottom: 1px solid #f8d5a0;
}

.model-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    background: rgba(0,0,0,0.08);
    color: #333;
}

.model-card p,
.model-card ul {
    padding: 0.7rem 1rem;
    margin: 0;
    font-size: 0.9rem;
    color: #444;
    line-height: 1.5;
}

.model-card ul {
    padding-top: 0;
    padding-left: 2rem;
}

.model-card li {
    margin-bottom: 0.3rem;
}

@media (max-width: 540px) {
    .model-cards {
        grid-template-columns: 1fr;
    }
}

.welcome-buttons {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1rem;
}

.welcome-action {
    display: flex;
    gap: 0.9rem;
    align-items: flex-start;
    padding: 1rem;
    border: 1px solid #e3e8f0;
    border-radius: 14px;
    background: #fbfbff;
}

.guide-btn {
    width: 40px;
    height: 40px;
    min-width: 40px;
    min-height: 40px;
    flex-shrink: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    border: 1px solid rgba(0, 0, 0, 0.1);
    background: #fff;
    color: #333;
    cursor: default;
    opacity: 1;
    transition: background-color 0.15s ease, box-shadow 0.15s ease;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.welcome-action .guide-btn i {
    font-size: 1.1rem;
    color: inherit;
}

.welcome-action .guide-btn.benchmark-icon-btn,
.welcome-action .guide-btn.benchmark-icon-btn:disabled {
    background-color: #1565c0 !important;
    color: #fff !important;
    border: none !important;
    box-shadow: 0 2px 6px rgba(21, 101, 192, 0.3) !important;
}

.welcome-action .guide-btn.import-icon-btn,
.welcome-action .guide-btn.import-icon-btn:disabled {
    background-color: #9c27b0 !important;
    color: #fff !important;
    border: none !important;
    box-shadow: 0 2px 6px rgba(156, 39, 176, 0.3) !important;
}

.guide-btn:disabled {
    opacity: 1;
    background: #fff;
    color: #333;
}

.welcome-action .guide-btn.random-icon-btn,
.welcome-action .guide-btn.random-icon-btn:disabled {
    background-color: #fff;
    color: #111;
}

.welcome-action .guide-btn.benchmark-icon-btn:disabled,
.welcome-action .guide-btn.import-icon-btn:disabled,
.welcome-action .guide-btn.copy-icon-btn:disabled,
.welcome-action .guide-btn.download-icon-btn:disabled,
.welcome-action .guide-btn.help-icon-btn:disabled,
.welcome-action .guide-btn.new-icon-btn:disabled,
.welcome-action .guide-btn.solve-icon-btn:disabled,
.welcome-action .guide-btn.reset-icon-btn:disabled {
    background: inherit;
}

.welcome-actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 1rem;
}

.welcome-actions .solve-btn {
    padding: 0.95rem 1.5rem;
}

.welcome-window kbd {
    display: inline-block;
    background: #f1f5f9;
    color: #1f2937;
    border: 1px solid #cbd5e1;
    border-bottom-width: 2px;
    padding: 0.1rem 0.45rem;
    border-radius: 5px;
    font-family: monospace;
    font-size: 0.82em;
}

.welcome-window code {
    background: #f1f5f9;
    color: #1f2937;
    padding: 0.15rem 0.4rem;
    border-radius: 6px;
    font-size: 0.92rem;
}

@media (max-width: 800px) {
    .welcome-buttons {
        grid-template-columns: 1fr;
    }
}

.solve-btn {
    padding: 1vh 2vw;
    font-size: 1rem;
    cursor: pointer;
    background-color: #4caf50;
    color: white;
    border: none;
    border-radius: 8px;
    transition: background-color 0.3s;
    margin-top: 2vh;
    font-weight: bold;
}

.solve-btn:hover:not(:disabled) {
    background-color: #45a049;
}

.solve-btn:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
}

.solve-icon-btn {
    background-color: #4caf50 !important;
    color: #fff !important;
    border: none;
    box-shadow: 0 2px 6px rgba(76, 175, 80, 0.3);
}

.reset-icon-btn {
    background-color: #d32f2f !important;
    color: #fff !important;
    border: none;
    box-shadow: 0 2px 6px rgba(211, 47, 47, 0.3);
}

.new-icon-btn {
    background-color: #ff9800 !important;
    color: #fff !important;
    border: none;
    box-shadow: 0 2px 6px rgba(255, 152, 0, 0.3);
}

.help-icon-btn {
    background-color: #00bcd4 !important;
    color: #fff !important;
    border: none;
    box-shadow: 0 2px 6px rgba(0, 188, 212, 0.3);
}

.copy-icon-btn {
    background-color: #2196f3 !important;
    color: #fff !important;
    border: none;
    box-shadow: 0 2px 6px rgba(33, 150, 243, 0.3);
}

.download-icon-btn {
    background-color: #ff6f00 !important;
    color: #fff !important;
    border: none;
    box-shadow: 0 2px 6px rgba(255, 111, 0, 0.3);
}
</style>
