// Recipe page JavaScript for individual recipe display
let allRecipes = [];
let currentRecipe = null;
let currentRecipeIndex = -1;

// Family information (matching the stemma classifications)
const familyInfo = {
    'A_Classical': {
        name: 'Family A: Classical & Renaissance',
        desc: 'The full gall-ink recipe tradition with soak-then-boil process',
        symbol: 'α',
        color: '#FF6B6B'
    },
    'B_LongSoak': {
        name: 'Family B: Long-Soak Lineage',
        desc: 'Innovation: Galls dropped, multi-day soaking required',
        symbol: 'β',
        color: '#4ECDC4'
    },
    'C_Modern': {
        name: 'Family C: Modern Baby',
        desc: 'Final synthesis: No galls, no soak, precise quantities',
        symbol: 'γ',
        color: '#45B7D1'
    },
    'D_SaltWaterBoil': {
        name: 'Family D: Salt-Water-Boil',
        desc: 'Parallel innovation: Direct salt water boil process',
        symbol: 'δ',
        color: '#96CEB4'
    },
    'E_Meta': {
        name: 'Family E: Meta-Witnesses',
        desc: 'Witnesses that test, analyze, or exist outside main tradition',
        symbol: 'ε',
        color: '#FFEAA7'
    },
    'F_Anomalous': {
        name: 'Family F: Anomalous Branch',
        desc: 'Separate branch where process is reversed (boil-then-write)',
        symbol: 'ζ',
        color: '#DDA0DD'
    },
    'G_Cepak': {
        name: 'Family G: Cépak Hybrid',
        desc: 'Modernized hybrid: Precise quantities added to gall-less recipe',
        symbol: 'η',
        color: '#98D8C8'
    }
};

// Language display names
const languageNames = {
    'grk': 'Greek (Ancient)',
    'grc': 'Greek (Ancient)',
    'lat': 'Latin',
    'deu': 'German',
    'fra': 'French',
    'ita': 'Italian',
    'eng': 'English',
    'unknown': 'Unknown Language'
};

document.addEventListener('DOMContentLoaded', async () => {
    // Get recipe ID from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const recipeId = urlParams.get('id');
    const returnContext = urlParams.get('from') || 'database'; // database, stemma, tree

    if (!recipeId) {
        showError('No recipe ID specified');
        return;
    }

    // Update back link based on context
    updateBackLink(returnContext);

    // Load data and display recipe
    await loadRecipeData();
    displayRecipe(recipeId);
});

async function loadRecipeData() {
    try {
        const response = await fetch('data/witnesses.json');
        if (response.ok) {
            allRecipes = await response.json();
            console.log(`Loaded ${allRecipes.length} recipes for recipe page`);
        } else {
            throw new Error(`Failed to load data: ${response.status}`);
        }
    } catch (error) {
        console.error('Error loading recipe data:', error);
        showError('Failed to load recipe data');
    }
}

function updateBackLink(context) {
    const backLink = document.getElementById('back-link');
    switch (context) {
        case 'stemma':
            backLink.href = 'stemma/stemma.html';
            backLink.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M19 12H5M12 19l-7-7 7-7"/>
                </svg>
                Back to Stemma
            `;
            break;
        case 'tree':
            backLink.href = 'stemma/tree.html';
            backLink.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M19 12H5M12 19l-7-7 7-7"/>
                </svg>
                Back to Tree View
            `;
            break;
        default:
            backLink.href = 'index.html';
            backLink.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M19 12H5M12 19l-7-7 7-7"/>
                </svg>
                Back to Database
            `;
    }
}

function displayRecipe(recipeId) {
    // Find the recipe
    currentRecipe = allRecipes.find(r => r.metadata?.witness_id === recipeId);

    if (!currentRecipe) {
        showError(`Recipe ${recipeId} not found`);
        return;
    }

    // Find recipe index for navigation
    currentRecipeIndex = allRecipes.findIndex(r => r.metadata?.witness_id === recipeId);

    // Hide loading, show content
    document.getElementById('loading-state').classList.add('hidden');
    document.getElementById('recipe-content').classList.remove('hidden');

    // Update page metadata and SEO
    updatePageMetadata();
    updateSEOMeta();

    // Populate content sections
    populateHeader();
    populateSourceInfo();
    populateTextContent();
    populateFamilyInfo();
    populateConfidence();
    populateIngredients();
    populateProcessSteps();
    populateDiagnosticVariants();
    populateRelatedRecipes();
    setupNavigation();
}

function updatePageMetadata() {
    const meta = currentRecipe.metadata || {};
    const title = `${meta.witness_id || 'Recipe'}: ${meta.source_work || 'Historical Egg Writing Recipe'}`;
    const description = `Historical egg writing recipe from ${meta.date || 'unknown date'} by ${meta.author || 'unknown author'}. ${currentRecipe.process_summary || ''} Part of the digital humanities analysis of invisible ink traditions.`;

    // Update page title and meta tags
    document.title = title;
    document.getElementById('page-title').content = title;
    document.getElementById('page-description').content = description;
    document.getElementById('page-keywords').content = `${meta.witness_id}, ${meta.author}, ${meta.language}, historical recipes, digital humanities, stemmatology`;

    // Update Open Graph tags
    document.getElementById('og-title').content = title;
    document.getElementById('og-description').content = description;
    document.getElementById('og-url').content = window.location.href;
}

function populateHeader() {
    const meta = currentRecipe.metadata || {};

    document.getElementById('header-witness-id').textContent = meta.witness_id || 'Unknown ID';
    document.getElementById('recipe-title').textContent = meta.source_work || 'Historical Recipe';
    document.getElementById('recipe-date').textContent = meta.date ? `${meta.date} CE` : 'Unknown Date';
    document.getElementById('recipe-author').textContent = meta.author || 'Unknown Author';
    document.getElementById('recipe-language').textContent = languageNames[meta.language] || meta.language || 'Unknown';

    // Family badge
    const family = classifyRecipe(currentRecipe);
    const familyData = familyInfo[family];
    if (familyData) {
        const familyBadge = document.getElementById('family-badge');
        familyBadge.textContent = `${familyData.symbol} ${familyData.name}`;
        familyBadge.style.backgroundColor = familyData.color;
    }

    // Confidence badge
    const confidence = getRecipeConfidence(currentRecipe);
    const confidenceBadge = document.getElementById('confidence-badge');
    if (confidence > 0) {
        confidenceBadge.textContent = `${Math.round(confidence * 100)}% Confidence`;
        confidenceBadge.style.backgroundColor = confidence > 0.8 ? '#1a7f37' : confidence > 0.5 ? '#f59e0b' : '#dc2626';
    } else {
        confidenceBadge.textContent = 'Confidence Not Assessed';
        confidenceBadge.style.backgroundColor = '#6b7280';
    }
}

function populateSourceInfo() {
    const meta = currentRecipe.metadata || {};

    document.getElementById('source-work').textContent = meta.source_work || 'Unknown Source';
    document.getElementById('recipe-genre').textContent = meta.genre || 'Unknown Genre';
    document.getElementById('language-full').textContent = languageNames[meta.language] || meta.language || 'Unknown';
    document.getElementById('source-attribution').textContent = currentRecipe.attribution?.source_name || 'Unattributed';

    // Handle URL if available
    const urlRow = document.getElementById('url-row');
    const url = currentRecipe.text_data?.url || currentRecipe.url;
    if (url && url !== '[URL Missing]') {
        document.getElementById('source-url').href = url;
        urlRow.style.display = 'flex';
    } else {
        urlRow.style.display = 'none';
    }
}

function populateTextContent() {
    const textSection = document.getElementById('text-section');
    const fullTextContent = document.getElementById('full-text-content');
    const translationText = document.getElementById('translation-text');
    const translationSection = document.getElementById('translation-content');

    const fullText = currentRecipe.text_data?.full_text || currentRecipe.full_text;
    if (fullText) {
        fullTextContent.textContent = fullText;
    } else {
        fullTextContent.innerHTML = '<em>Original text not available</em>';
    }

    const translation = currentRecipe.text_data?.translation || currentRecipe.translation;
    if (translation && translation.trim()) {
        translationText.textContent = translation;
        translationSection.style.display = 'block';
    } else {
        translationSection.style.display = 'none';
    }
}


function populateFamilyInfo() {
    const family = classifyRecipe(currentRecipe);
    const familyData = familyInfo[family];

    if (familyData) {
        document.getElementById('family-symbol').textContent = familyData.symbol;
        document.getElementById('family-symbol').style.backgroundColor = familyData.color;
        document.getElementById('family-name').textContent = familyData.name;
        document.getElementById('family-description').textContent = familyData.desc;
    }
}

function populateConfidence() {
    const confidence = getRecipeConfidence(currentRecipe);
    const confidenceFill = document.getElementById('confidence-fill');
    const confidenceText = document.getElementById('confidence-text');
    const confidenceDetails = document.getElementById('confidence-details');

    if (confidence > 0) {
        const percentage = Math.round(confidence * 100);
        confidenceFill.style.width = `${percentage}%`;
        confidenceText.textContent = `${percentage}%`;

        // Add confidence details if available
        const analysisConf = currentRecipe.analysis_confidence;
        if (analysisConf) {
            let details = `<p><strong>${percentage}% overall confidence</strong> in this analysis.</p>`;

            if (analysisConf.uncertainty_flags && analysisConf.uncertainty_flags.length > 0) {
                details += `<p><strong>Uncertainty factors:</strong> ${analysisConf.uncertainty_flags.join(', ')}</p>`;
            }

            if (analysisConf.text_completeness) {
                details += `<p><strong>Text completeness:</strong> ${Math.round(analysisConf.text_completeness * 100)}%</p>`;
            }

            confidenceDetails.innerHTML = details;
        } else {
            confidenceDetails.innerHTML = `<p>${percentage}% confidence in analysis and classification.</p>`;
        }
    } else {
        confidenceFill.style.width = '0%';
        confidenceText.textContent = 'N/A';
        confidenceDetails.innerHTML = '<p>No confidence assessment available for this recipe.</p>';
    }
}

function populateIngredients() {
    const ingredientsElement = document.getElementById('ingredients-list');
    const ingredients = currentRecipe.ingredients;

    if (ingredients && ingredients.primary_components && ingredients.primary_components.length > 0) {
        const list = ingredients.primary_components.map(comp => {
            const quantity = comp.quantity ? ` (${comp.quantity})` : '';
            return `<div class="ingredient-item">${comp.substance}${quantity}</div>`;
        }).join('');
        ingredientsElement.innerHTML = list;
    } else {
        ingredientsElement.innerHTML = '<em>Ingredient information not available</em>';
    }
}

function populateProcessSteps() {
    const processElement = document.getElementById('process-steps-list');
    const processSteps = currentRecipe.process_steps;

    if (processSteps && processSteps.preparation_sequence && processSteps.preparation_sequence.length > 0) {
        const steps = processSteps.preparation_sequence.map((step, index) => {
            return `<div class="process-step">
                <div class="step-number">${index + 1}</div>
                <div class="step-content">
                    <strong>${step.action}</strong>
                    ${step.details ? `<p>${step.details}</p>` : ''}
                </div>
            </div>`;
        }).join('');
        processElement.innerHTML = steps;
    } else {
        processElement.innerHTML = '<em>Detailed process steps not available</em>';
    }
}

function populateDiagnosticVariants() {
    const variantsElement = document.getElementById('diagnostic-variants');
    const variants = [];

    // Extract diagnostic variants from ingredients and process
    if (currentRecipe.ingredients && currentRecipe.ingredients.diagnostic_variants) {
        const ing = currentRecipe.ingredients.diagnostic_variants;
        Object.entries(ing).forEach(([key, value]) => {
            if (value && value !== 'unknown') {
                variants.push({
                    feature: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
                    value: value.replace(/_/g, ' ')
                });
            }
        });
    }

    if (currentRecipe.process_steps && currentRecipe.process_steps.critical_variants) {
        const proc = currentRecipe.process_steps.critical_variants;
        Object.entries(proc).forEach(([key, value]) => {
            if (value && value !== 'unknown') {
                variants.push({
                    feature: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
                    value: String(value).replace(/_/g, ' ')
                });
            }
        });
    }

    if (variants.length > 0) {
        const list = variants.map(variant => {
            return `<div class="variant-item">
                <label>${variant.feature}:</label>
                <span>${variant.value}</span>
            </div>`;
        }).join('');
        variantsElement.innerHTML = list;
    } else {
        variantsElement.innerHTML = '<em>Diagnostic variant information not available</em>';
    }
}

function populateRelatedRecipes() {
    const relatedElement = document.getElementById('related-recipes');
    const currentFamily = classifyRecipe(currentRecipe);
    const currentDate = currentRecipe.metadata?.date || 0;

    // Find related recipes (same family or similar time period)
    const related = allRecipes.filter(recipe => {
        if (recipe.metadata?.witness_id === currentRecipe.metadata?.witness_id) return false;

        const recipeFamily = classifyRecipe(recipe);
        const recipeDate = recipe.metadata?.date || 0;

        // Same family or within 100 years
        return recipeFamily === currentFamily || Math.abs(recipeDate - currentDate) <= 100;
    }).slice(0, 6); // Limit to 6 related recipes

    if (related.length > 0) {
        const cards = related.map(recipe => {
            const meta = recipe.metadata || {};
            const family = classifyRecipe(recipe);
            const familyData = familyInfo[family];

            return `<a href="recipe.html?id=${meta.witness_id}" class="related-card">
                <div class="related-header">
                    <span class="related-id">${meta.witness_id}</span>
                    <span class="related-family" style="background: ${familyData?.color || '#ccc'}">${familyData?.symbol || '?'}</span>
                </div>
                <h4>${meta.source_work || 'Historical Recipe'}</h4>
                <div class="related-meta">
                    <span>${meta.date || 'Unknown'} CE</span>
                    <span>${meta.author || 'Unknown Author'}</span>
                </div>
            </a>`;
        }).join('');

        relatedElement.innerHTML = cards;
    } else {
        relatedElement.innerHTML = '<em>No related recipes found</em>';
    }
}

function setupNavigation() {
    // Previous/Next recipe navigation
    const prevBtn = document.getElementById('prev-recipe');
    const nextBtn = document.getElementById('next-recipe');
    const footerPrev = document.getElementById('footer-prev');
    const footerNext = document.getElementById('footer-next');

    // Find adjacent recipes
    const prevRecipe = currentRecipeIndex > 0 ? allRecipes[currentRecipeIndex - 1] : null;
    const nextRecipe = currentRecipeIndex < allRecipes.length - 1 ? allRecipes[currentRecipeIndex + 1] : null;

    // Setup previous navigation
    if (prevRecipe) {
        const prevId = prevRecipe.metadata?.witness_id;
        const prevTitle = prevRecipe.metadata?.source_work || 'Historical Recipe';

        prevBtn.disabled = false;
        prevBtn.onclick = () => navigateToRecipe(prevId);
        footerPrev.disabled = false;
        footerPrev.onclick = () => navigateToRecipe(prevId);
        document.getElementById('prev-title').textContent = `${prevId}: ${prevTitle.substring(0, 30)}${prevTitle.length > 30 ? '...' : ''}`;
    } else {
        prevBtn.disabled = true;
        footerPrev.disabled = true;
        document.getElementById('prev-title').textContent = 'No previous recipe';
    }

    // Setup next navigation
    if (nextRecipe) {
        const nextId = nextRecipe.metadata?.witness_id;
        const nextTitle = nextRecipe.metadata?.source_work || 'Historical Recipe';

        nextBtn.disabled = false;
        nextBtn.onclick = () => navigateToRecipe(nextId);
        footerNext.disabled = false;
        footerNext.onclick = () => navigateToRecipe(nextId);
        document.getElementById('next-title').textContent = `${nextId}: ${nextTitle.substring(0, 30)}${nextTitle.length > 30 ? '...' : ''}`;
    } else {
        nextBtn.disabled = true;
        footerNext.disabled = true;
        document.getElementById('next-title').textContent = 'No next recipe';
    }
}

function navigateToRecipe(recipeId) {
    const currentUrl = new URL(window.location);
    currentUrl.searchParams.set('id', recipeId);
    window.location.href = currentUrl.toString();
}

function showError(message) {
    document.getElementById('loading-state').classList.add('hidden');
    document.getElementById('error-state').classList.remove('hidden');
    console.error('Recipe page error:', message);
}

// Helper functions (from the main app)
function classifyRecipe(recipe) {
    const id = recipe.metadata?.witness_id;
    const ingredients = recipe.ingredients?.diagnostic_variants;
    const process = recipe.process_steps?.critical_variants;

    if (!id || !ingredients || !process) {
        return 'E_Meta';
    }

    // Handle outliers first
    if (['W23', 'W27', 'W37', 'W74', 'W87'].includes(id)) return 'E_Meta';
    if (process.boiling_timing === 'before_writing') return 'F_Anomalous';
    if (id === 'W57') return 'G_Cepak';

    // Main classifications
    const hasSaltWaterBoil = recipe.process_steps?.preparation_sequence?.some(s =>
        s.details && (s.details.toLowerCase().includes('salt water') || s.details.toLowerCase().includes('salzwasser'))
    ) || false;

    if (ingredients.gall_presence === 'present' && process.soaking_duration !== 'days' && hasSaltWaterBoil) {
        return 'D_SaltWaterBoil';
    }
    if (ingredients.gall_presence === 'absent' && process.soaking_duration === 'days') {
        return 'B_LongSoak';
    }
    if (ingredients.gall_presence === 'absent' && process.soaking_duration !== 'days') {
        return 'C_Modern';
    }
    if (ingredients.gall_presence === 'present') {
        return 'A_Classical';
    }

    return 'E_Meta';
}

function updateSEOMeta() {
    if (!currentRecipe) return;

    const witnessId = currentRecipe.metadata?.witness_id || 'Unknown Recipe';
    const author = currentRecipe.metadata?.author || 'Unknown Author';
    const date = currentRecipe.metadata?.date || 'Unknown Date';
    const sourceWork = currentRecipe.metadata?.source_work || 'Unknown Source';
    const family = classifyRecipe(currentRecipe);
    const familyData = familyInfo[family] || { name: 'Unknown Family' };

    // Update page title
    const pageTitle = `${witnessId}: ${sourceWork} (${date}) - Historical Egg Writing Recipes`;
    document.getElementById('page-title').textContent = pageTitle;
    document.title = pageTitle;

    // Update meta description
    const description = `Historical egg writing recipe ${witnessId} by ${author} from ${sourceWork} (${date}). Part of ${familyData.name} in the stemma classification.`;
    document.getElementById('page-description').setAttribute('content', description);

    // Update keywords
    const keywords = `${witnessId}, ${author}, ${sourceWork}, ${date}, historical recipes, egg writing, stemma, ${familyData.name}, digital humanities`;
    document.getElementById('page-keywords').setAttribute('content', keywords);

    // Update Open Graph tags
    document.getElementById('og-title').setAttribute('content', pageTitle);
    document.getElementById('og-description').setAttribute('content', description);

    // Update canonical URL
    const currentUrl = window.location.href;
    document.getElementById('og-url').setAttribute('content', currentUrl);
}

function getRecipeConfidence(recipe) {
    try {
        // Try recipe.confidence first, then analysis_confidence.overall_confidence
        const a = recipe.confidence && recipe.confidence > 0 ? Number(recipe.confidence) : undefined;
        const b = recipe.analysis_confidence?.overall_confidence ? Number(recipe.analysis_confidence.overall_confidence) : undefined;

        const value = (a !== undefined && a > 0) ? a : (b !== undefined ? b : 0);
        return Math.max(0, Math.min(1, value));
    } catch (error) {
        console.error('Error calculating confidence:', error);
        return 0;
    }
}

// Keyboard navigation
document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft' && !document.getElementById('prev-recipe').disabled) {
        document.getElementById('prev-recipe').click();
    } else if (e.key === 'ArrowRight' && !document.getElementById('next-recipe').disabled) {
        document.getElementById('next-recipe').click();
    } else if (e.key === 'Escape') {
        // Go back to previous page
        window.history.back();
    }
});