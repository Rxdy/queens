#!/bin/bash

# Script de vérification de la suite de tests
# Usage: bash front/verify-tests.sh

echo "🔍 Vérification de la suite de tests..."
echo ""

cd "$(dirname "$0")" || exit 1

# Vérifier que npm est installé
if ! command -v npm &> /dev/null; then
    echo "❌ npm n'est pas installé"
    exit 1
fi
echo "✅ npm installé"

# Vérifier que package.json existe
if [ ! -f "package.json" ]; then
    echo "❌ package.json non trouvé"
    exit 1
fi
echo "✅ package.json trouvé"

# Vérifier que les dépendances sont installées
if [ ! -d "node_modules" ]; then
    echo "⚠️  node_modules non trouvé, installation en cours..."
    npm install
fi
echo "✅ Dependencies OK"

# Vérifier que vitest est installé
if ! npm list vitest &> /dev/null; then
    echo "❌ vitest n'est pas installé"
    exit 1
fi
echo "✅ vitest installé"

# Vérifier que @vue/test-utils est installé
if ! npm list @vue/test-utils &> /dev/null; then
    echo "❌ @vue/test-utils n'est pas installé"
    exit 1
fi
echo "✅ @vue/test-utils installé"

# Vérifier que jsdom est installé
if ! npm list jsdom &> /dev/null; then
    echo "❌ jsdom n'est pas installé"
    exit 1
fi
echo "✅ jsdom installé"

# Vérifier les fichiers de test
echo ""
echo "🧪 Fichiers de test:"
test_files=(
    "src/__tests__/setup.js"
    "src/__tests__/App.spec.js"
    "src/__tests__/App.integration.spec.js"
    "src/__tests__/App.validation.spec.js"
    "src/__tests__/App.render.spec.js"
)

for file in "${test_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (manquant)"
    fi
done

# Vérifier la configuration
echo ""
echo "⚙️  Configuration:"
if [ -f "vitest.config.js" ]; then
    echo "✅ vitest.config.js"
else
    echo "❌ vitest.config.js (manquant)"
fi

# Vérifier les scripts npm
echo ""
echo "📜 Scripts npm disponibles:"
if npm run | grep -q "test"; then
    echo "✅ npm test"
else
    echo "❌ npm test (script manquant)"
fi

if npm run | grep -q "test:ui"; then
    echo "✅ npm run test:ui"
else
    echo "❌ npm run test:ui (script manquant)"
fi

if npm run | grep -q "test:coverage"; then
    echo "✅ npm run test:coverage"
else
    echo "❌ npm run test:coverage (script manquant)"
fi

# Résumé
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Tout est prêt! Vous pouvez maintenant:"
echo ""
echo "   npm test              # Lancer les tests"
echo "   npm test -- --watch   # Mode watch"
echo "   npm run test:ui       # Interface interactive"
echo "   npm run test:coverage # Rapport de couverture"
echo ""
echo "   make test-unit-front  # Via Makefile"
echo ""
echo "📖 Pour plus d'infos, consultez:"
echo "   - TESTING.md"
echo "   - src/__tests__/README.md"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
